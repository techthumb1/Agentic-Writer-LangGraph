# WriterzRoom Deployment Guide

## Quick Deploy Options

### Option 1: GCP Cloud Run (Production - 45 minutes)

```bash
# Deploy infrastructure
cd terraform && terraform apply -var="project_id=agentic-writer"

# Add secrets
echo -n "sk-..." | gcloud secrets versions add openai-key --data-file=-

# Deploy
gcloud builds submit --config cloudbuild.yaml
```

### Option 2: Docker Compose (Local/Testing)

```bash
cp .env.example .env
nano .env  # Add API keys
docker-compose up -d
```

---

## Prerequisites

### Required API Keys

- **OpenAI** (required): <https://platform.openai.com/api-keys>
- **Anthropic** (optional): <https://console.anthropic.com/>
- **Tavily** (for research): <https://app.tavily.com/>

### Required Services

- **GCP Account** with billing enabled
- **Domain**: writerzroom.com
- **Google OAuth**: <https://console.cloud.google.com/>

---

## Production Deployment (GCP)

### 1. Initial Setup (10 min)

```bash
export PROJECT_ID="agentic-writer"
gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Infrastructure (15 min)

```bash
cd terraform
terraform init
terraform apply -var="project_id=agentic-writer"
```

Creates:

- Cloud Run (2 vCPU, 8GB, autoscale 1-50)
- Cloud SQL Postgres (HA, 2vCPU/8GB, PITR)
- Memorystore Redis (2GB, HA)
- VPC + Secret Manager

### 3. Add Secrets (5 min)

```bash
# OpenAI
echo -n "sk-..." | gcloud secrets versions add openai-key --data-file=-

# Anthropic
echo -n "sk-ant-..." | gcloud secrets versions add anthropic-key --data-file=-

# App secret
openssl rand -base64 32 | gcloud secrets versions add secret-key --data-file=-
```

### 4. Deploy Backend (10 min)

```bash
gcloud builds submit --config cloudbuild.yaml
```

### 5. Custom Domain (5 min)

```bash
gcloud run domain-mappings create \
  --service writerzroom-backend \
  --domain api.writerzroom.com \
  --region us-central1
```

Add to DNS:

- Type: CNAME
- Host: api
- Value: ghs.googlehosted.com

### 6. Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

Set env vars in Vercel:

```bash
NEXT_PUBLIC_API_URL=https://api.writerzroom.com
NEXTAUTH_URL=https://writerzroom.com
NEXTAUTH_SECRET=<generate-with-openssl>
DATABASE_URL=<from-cloud-sql>
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### 7. Database Migrations

```bash
cd frontend
npx prisma migrate deploy
```

---

## Environment Variables

### Backend (Cloud Run - via Secret Manager)

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<generated>
```

### Frontend (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://api.writerzroom.com
NEXTAUTH_SECRET=<generated>
NEXTAUTH_URL=https://writerzroom.com
DATABASE_URL=postgresql://...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## Health Checks

```bash
# Backend
curl https://api.writerzroom.com/health

# Expected: {"status":"healthy","services":{...}}
```

---

## Monitoring

### Cloud Console

- Cloud Run: Logs, metrics, traces
- Error Reporting: Automatic error tracking
- Cloud SQL: Connection stats

### Alerts

```bash
gcloud monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --alert-strategy=condition \
  --condition-threshold-value=0.05
```

---

## Scaling

### Cloud Run

Already configured in `cloudbuild.yaml`:

- Min instances: 1
- Max instances: 50
- Concurrency: 12
- Memory: 8GB
- CPU: 2 vCPU

### Auto-scaling triggers

- CPU utilization > 60%
- Request queue depth > 10

---

## Rollback

```bash
# List revisions
gcloud run revisions list --service writerzroom-backend --region us-central1

# Rollback
gcloud run services update-traffic writerzroom-backend \
  --to-revisions PREVIOUS_REVISION=100 --region us-central1
```

---

## Cost Estimates

### Beta Phase (100 requests/day)

- Cloud Run: Free tier
- Cloud SQL: ~$70/month
- Redis: ~$65/month
- **Total: ~$135/month**

### Production (1000+ requests/day)

- Cloud Run: ~$50/month
- Cloud SQL: ~$70/month
- Redis: ~$65/month
- **Total: ~$185/month**

Plus OpenAI API usage (variable)

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
gcloud run services logs read writerzroom-backend --region us-central1

# Common issues:
# - Missing secrets
# - VPC connector not attached
# - Database connection failed
```

### Frontend build fails

```bash
node -v  # Check version 18+
rm -rf .next node_modules
npm install
npm run build
```

### Database connection errors

```bash
# Test connection
gcloud sql connect writerzroom-db --user=writerzroom_user

# Run migrations
npx prisma migrate deploy
```

---

## Security Checklist

- [ ] All secrets in Secret Manager
- [ ] VPC private networking enabled
- [ ] CORS configured for production domains
- [ ] HTTPS enforced
- [ ] IAM least-privilege roles
- [ ] Database backups enabled (PITR)
- [ ] Error tracking configured
- [ ] Rate limiting enabled

---

## Support

- **Documentation**: <https://docs.writerzroom.com>
- **Issues**: <https://github.com/yourusername/writerzroom/issues>
- **GCP Status**: <https://status.cloud.google.com>
