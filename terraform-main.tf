# terraform/main.tf - GCP Infrastructure as Code

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
}

variable "region" {
  default = "us-central1"
}

# Enable APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "vpcaccess.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
  ])
  service = each.key
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "writerzroom-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "writerzroom-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# VPC Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "writerzroom-connector"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  
  depends_on = [google_project_service.services]
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "postgres" {
  name             = "writerzroom-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-custom-2-8192"
    availability_type = "REGIONAL"
    disk_size         = 200
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "02:00"
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
  }

  deletion_protection = true
  
  depends_on = [google_project_service.services]
}

resource "google_sql_database" "database" {
  name     = "writerzroom"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "writerzroom_user"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Memorystore (Redis)
resource "google_redis_instance" "cache" {
  name           = "writerzroom-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = 2
  region         = var.region
  
  authorized_network = google_compute_network.vpc.id
  
  redis_version = "REDIS_7_0"
  display_name  = "WriterzRoom Cache"
  
  depends_on = [google_project_service.services]
}

# Artifact Registry
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "writerzroom"
  format        = "DOCKER"
  
  depends_on = [google_project_service.services]
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "secrets" {
  for_each = toset([
    "openai-key",
    "anthropic-key",
    "secret-key",
  ])
  
  secret_id = each.key
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.services]
}

# Service Account for Cloud Run
resource "google_service_account" "backend" {
  account_id   = "writerzroom-backend"
  display_name = "WriterzRoom Backend Service Account"
}

# IAM - Secret Manager access
resource "google_secret_manager_secret_iam_member" "backend_secrets" {
  for_each = google_secret_manager_secret.secrets
  
  secret_id = each.value.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend.email}"
}

# IAM - Cloud SQL client
resource "google_project_iam_member" "backend_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Outputs
output "vpc_connector" {
  value = google_vpc_access_connector.connector.id
}

output "database_connection" {
  value     = google_sql_database_instance.postgres.connection_name
  sensitive = true
}

output "redis_host" {
  value = google_redis_instance.cache.host
}

output "service_account_email" {
  value = google_service_account.backend.email
}
