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
    "vpcaccess.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "servicenetworking.googleapis.com",
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

# Private IP for Cloud SQL
resource "google_compute_global_address" "private_ip" {
  name          = "writerzroom-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Private Service Connection
resource "google_service_networking_connection" "private_vpc" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip.name]
  
  depends_on = [google_project_service.services]
}

# VPC Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "writerzroom-connector"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  
  depends_on = [google_project_service.services]
}

# Cloud SQL (PostgreSQL 16)
resource "google_sql_database_instance" "postgres" {
  name             = "writerzroom-db"
  database_version = "POSTGRES_16"
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
  
  depends_on = [
    google_project_service.services,
    google_service_networking_connection.private_vpc
  ]
}

resource "google_sql_database" "database" {
  name     = "ai_content_db"
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


# Artifact Registry
resource "google_artifact_registry_repository" "repo" {
  location      = "us-central1"
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
    "database-url",
    "tavily-key",
    "auth-secret",
    "google-oauth-id",
    "google-oauth-secret",
    "fastapi-key",
    "backend-secret-key",
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

resource "google_service_account" "frontend" {
  account_id   = "writerzroom-frontend"
  display_name = "WriterzRoom Frontend Service Account"
}

# IAM - Secret Manager access (Backend)
resource "google_secret_manager_secret_iam_member" "backend_secrets" {
  for_each = google_secret_manager_secret.secrets
  
  secret_id = each.value.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend.email}"
}

# IAM - Secret Manager access (Frontend)
resource "google_secret_manager_secret_iam_member" "frontend_secrets" {
  for_each = toset([
    "auth-secret",
    "google-oauth-id",
    "google-oauth-secret",
    "database-url",
  ])
  
  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.frontend.email}"
}

# IAM - Cloud SQL client (Backend)
resource "google_project_iam_member" "backend_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# IAM - Cloud SQL client (Frontend)
resource "google_project_iam_member" "frontend_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# Outputs
output "vpc_connector" {
  value = google_vpc_access_connector.connector.id
}

output "database_connection" {
  value     = google_sql_database_instance.postgres.connection_name
  sensitive = true
}

output "database_private_ip" {
  value     = google_sql_database_instance.postgres.private_ip_address
  sensitive = true
}

output "backend_service_account_email" {
  value = google_service_account.backend.email
}

output "frontend_service_account_email" {
  value = google_service_account.frontend.email
}

output "artifact_registry_url" {
  value = "${google_artifact_registry_repository.repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}
