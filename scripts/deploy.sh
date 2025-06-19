#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
echo "🚀 Deploying to $ENVIRONMENT environment..."

# Build and deploy
docker-compose up -d --build

# Health checks
echo "Running health checks..."
sleep 30

if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

echo "🎉 Deployment to $ENVIRONMENT completed successfully!"
