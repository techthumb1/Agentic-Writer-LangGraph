# langgraph_app/monitoring/health.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import psycopg2
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

def check_api_keys() -> Dict[str, Any]:
    """Verify required API keys are configured"""
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
    """Enterprise health check - database and API keys only"""
    services = {
        "database": check_database(),
        "api_keys": check_api_keys()
    }
    
    overall_status = "healthy"
    for svc in services.values():
        if svc["status"] != "healthy":
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
    """Kubernetes readiness probe - requires healthy database"""
    db_ok = check_database()["status"] == "healthy"
    if db_ok:
        return {"status": "ready"}
    return {"status": "not_ready"}, 503