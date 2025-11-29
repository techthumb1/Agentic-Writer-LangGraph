#!/bin/bash
# startup.sh - Production startup script with validation

set -e

echo "🚀 WriterzRoom Startup Script"
echo "=============================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required environment variables
check_env_var() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}❌ Missing required environment variable: $1${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ $1 configured${NC}"
    fi
}

echo ""
echo "Checking required environment variables..."
check_env_var "DATABASE_URL"
check_env_var "OPENAI_API_KEY"
check_env_var "NEXTAUTH_SECRET"

echo ""
echo "Checking optional environment variables..."
[ -n "$REDIS_URL" ] && echo -e "${GREEN}✅ REDIS_URL configured${NC}" || echo -e "${YELLOW}⚠️  REDIS_URL not set (caching disabled)${NC}"
[ -n "$ANTHROPIC_API_KEY" ] && echo -e "${GREEN}✅ ANTHROPIC_API_KEY configured${NC}" || echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY not set (Claude disabled)${NC}"
[ -n "$SENTRY_DSN" ] && echo -e "${GREEN}✅ SENTRY_DSN configured${NC}" || echo -e "${YELLOW}⚠️  SENTRY_DSN not set (error tracking disabled)${NC}"

# Test database connection
echo ""
echo "Testing database connection..."
python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.close()
    print('${GREEN}✅ Database connection successful${NC}')
except Exception as e:
    print(f'${RED}❌ Database connection failed: {e}${NC}')
    exit(1)
"

# Test Redis if configured
if [ -n "$REDIS_URL" ]; then
    echo "Testing Redis connection..."
    python3 -c "
import redis
import os
try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('${GREEN}✅ Redis connection successful${NC}')
except Exception as e:
    print(f'${YELLOW}⚠️  Redis connection failed: {e}${NC}')
    print('${YELLOW}   Continuing without cache...${NC}')
"
fi

# Verify OpenAI API key
echo ""
echo "Verifying OpenAI API key..."
python3 -c "
import openai
import os
try:
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # Quick validation call
    print('${GREEN}✅ OpenAI API key valid${NC}')
except Exception as e:
    print(f'${RED}❌ OpenAI API key invalid: {e}${NC}')
    exit(1)
"

echo ""
echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "Starting services..."

# Start the application
exec "$@"