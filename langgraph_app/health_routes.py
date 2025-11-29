# langgraph_app/health_routes.py
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import asyncpg, redis.asyncio as redis, os


router = APIRouter()

@router.get("/api/healthz", tags=["Health"])
async def healthz():
    """Liveness check"""
    return JSONResponse({"status": "ok"}, status_code=status.HTTP_200_OK)

@router.get("/api/readyz", tags=["Health"])
async def readyz():
    """Readiness check: verifies DB and Redis connectivity"""
    db_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")
    try:
        # DB check
        conn = await asyncpg.connect(db_url)
        await conn.execute("SELECT 1")
        await conn.close()

        # Redis check
        redis_client = await redis.from_url(redis_url)
        await redis_client.ping()
        await redis_client.close()

        return JSONResponse({"status": "ready"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(
            {"status": "unready", "error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
