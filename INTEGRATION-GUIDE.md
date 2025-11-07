# Integration Guide: Adding Security to integrated_server.py

## Step 1: Copy Security Files

```bash
# Copy to project
cp security_middleware.py langgraph_app/middleware/
cp health_monitoring.py langgraph_app/monitoring/

# Create __init__.py files
touch langgraph_app/middleware/__init__.py
touch langgraph_app/monitoring/__init__.py
```

## Step 2: Update integrated_server.py

Add at top (after existing imports):

```python
from langgraph_app.middleware.security import setup_security_middleware, limiter
from langgraph_app.monitoring.health import router as health_router
```

Before `app = FastAPI()`, configure:

```python
# Initialize app with rate limiter
app = FastAPI(
    title="WriterzRoom API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG_MODE") == "true" else None,
)

# Setup security middleware
setup_security_middleware(app)

# Add health check routes
app.include_router(health_router, prefix="/api", tags=["health"])
```

Add rate limits to generation endpoint:

```python
@app.post("/api/generate-content")
@limiter.limit("10/minute")  # Add this decorator
async def generate_content(request: Request, ...):
    # existing code
```

## Step 3: Update requirements.txt

Add to project root requirements.txt:

```text
slowapi>=0.1.9
```

## Step 4: Update .env

Add:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
ALLOWED_ORIGINS=http://localhost:3000,https://writerzroom.com
```

## Step 5: Test Locally

```bash
# Install new dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn langgraph_app.integrated_server:app --reload

# Test health endpoint
curl http://localhost:8000/api/health

# Test rate limiting (send >10 requests)
for i in {1..15}; do curl http://localhost:8000/api/generate-content; done
```

## Expected Outputs

Health check:

```json
{
  "status": "healthy",
  "timestamp": 1699999999.999,
  "services": {
    "database": {"status": "healthy", "latency_ms": 23.4},
    "redis": {"status": "healthy", "latency_ms": 1.2},
    "api_keys": {"status": "healthy"}
  }
}
```

Rate limit response:

```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] `/api/health` returns 200 OK
- [ ] Rate limiting triggers after 10 requests
- [ ] CORS headers present in responses
- [ ] Security headers present (X-Content-Type-Options, etc.)
- [ ] Request logging appears in console

Done! Security middleware integrated.
