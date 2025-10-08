# File: langgraph_app/analytics_endpoints.py
from datetime import datetime, timedelta
from sqlalchemy import func, select, Float, Integer
from sqlalchemy.orm import Session
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Literal
import logging

from langgraph_app.database.models import GenerationLog, get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/insights")
async def get_analytics_insights(
    range: Literal["7d", "30d", "90d"] = Query(default="30d"),
    db: Session = Depends(get_db)
):
    logger.info(f"Analytics insights requested for range: {range}")
    
    days = {"7d": 7, "30d": 30, "90d": 90}[range]
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    total_gens = db.scalar(select(func.count(GenerationLog.id)).where(GenerationLog.created_at >= cutoff))
    
    if not total_gens:
        raise HTTPException(status_code=404, detail="No generation data available")
    
    total_words = db.scalar(select(func.sum(GenerationLog.word_count)).where(GenerationLog.created_at >= cutoff)) or 0
    avg_time = db.scalar(select(func.avg(GenerationLog.generation_time_seconds)).where(GenerationLog.created_at >= cutoff)) or 0
    success_rate = db.scalar(
        select(func.avg(GenerationLog.success.cast(Integer).cast(Float)))
        .where(GenerationLog.created_at >= cutoff)
    ) or 0
    most_used = db.execute(
        select(GenerationLog.template_id, func.count().label('count'))
        .where(GenerationLog.created_at >= cutoff)
        .group_by(GenerationLog.template_id)
        .order_by(func.count().desc())
        .limit(1)
    ).first()
    
    return {
        "totalGenerations": total_gens,
        "totalWords": total_words,
        "avgGenerationTime": round(avg_time, 2),
        "mostUsedTemplate": most_used[0] if most_used else None,
        "successRate": round(success_rate * 100, 2),
        "timeRange": range
    }