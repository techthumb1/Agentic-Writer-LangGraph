# langgraph_app/monitoring/health.py
"""
Production health checks and monitoring
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import psycopg2
import redis
import os
import time

router = APIRouter()

class HealthStatus(BaseModel):
    status: str
    timestamp: float
    services: Dict[str, Any]

def check_database() -> Dict[str, Any]:
    """Check PostgreSQL connection"""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.close()
        return {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_redis() -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        start = time.time()
        r.ping()
        latency = (time.time() - start) * 1000
        return {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_api_keys() -> Dict[str, Any]:
    """Verify API keys are configured"""
    keys = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "tavily": bool(os.getenv("TAVILY_API_KEY"))
    }
    
    if not keys["openai"]:
        return {"status": "unhealthy", "error": "OpenAI API key missing"}
    
    return {"status": "healthy", "keys_configured": keys}

@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Comprehensive health check"""
    services = {
        "database": check_database(),
        "redis": check_redis(),
        "api_keys": check_api_keys()
    }
    
    # Determine overall status
    overall_status = "healthy"
    for service_status in services.values():
        if service_status.get("status") != "healthy":
            overall_status = "unhealthy"
            break
    
    return HealthStatus(
        status=overall_status,
        timestamp=time.time(),
        services=services
    )

@router.get("/health/liveness")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@router.get("/health/readiness")
async def readiness():
    """Kubernetes readiness probe"""
    db_ok = check_database()["status"] == "healthy"
    redis_ok = check_redis()["status"] == "healthy"
    
    if db_ok and redis_ok:
        return {"status": "ready"}
    
    return {"status": "not_ready"}, 503