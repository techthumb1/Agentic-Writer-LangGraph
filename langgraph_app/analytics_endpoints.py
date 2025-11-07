# File: langgraph_app/analytics_endpoints.py
from datetime import datetime, timedelta
from sqlalchemy import func, select, Float, Integer, extract
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
        return {
            "totalGenerations": 0,
            "totalWords": 0,
            "avgGenerationTime": 0,
            "mostUsedTemplate": None,
            "successRate": 0,
            "timeRange": range
        }    
    
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

@router.get("/templates")
async def get_template_analytics(
    range: Literal["7d", "30d", "90d"] = Query(default="30d"),
    db: Session = Depends(get_db)
):
    """Template usage breakdown"""
    days = {"7d": 7, "30d": 30, "90d": 90}[range]
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    results = db.execute(
        select(
            GenerationLog.template_id,
            func.count(GenerationLog.id).label('usage_count'),
            func.avg(GenerationLog.generation_time_seconds).label('avg_time'),
            func.avg(GenerationLog.success.cast(Integer).cast(Float)).label('success_rate'),
            func.sum(GenerationLog.word_count).label('total_words')
        )
        .where(GenerationLog.created_at >= cutoff)
        .group_by(GenerationLog.template_id)
        .order_by(func.count(GenerationLog.id).desc())
    ).all()
    
    return {
        "templates": [
            {
                "id": r.template_id,
                "name": r.template_id.replace('_', ' ').title(),
                "usageCount": r.usage_count,
                "avgTime": round(r.avg_time, 2),
                "successRate": round(r.success_rate * 100, 2),
                "totalWords": r.total_words
            }
            for r in results
        ],
        "timeRange": range
    }

@router.get("/performance")
async def get_performance_analytics(
    range: Literal["7d", "30d", "90d"] = Query(default="30d"),
    db: Session = Depends(get_db)
):
    """Performance metrics over time"""
    days = {"7d": 7, "30d": 30, "90d": 90}[range]
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Daily aggregations
    daily_stats = db.execute(
        select(
            func.date_trunc('day', GenerationLog.created_at).label('date'),
            func.count(GenerationLog.id).label('count'),
            func.avg(GenerationLog.generation_time_seconds).label('avg_time'),
            func.sum(func.cast(GenerationLog.success, Integer)).label('successes')
        )
        .where(GenerationLog.created_at >= cutoff)
        .group_by(func.date_trunc('day', GenerationLog.created_at))
        .order_by(func.date_trunc('day', GenerationLog.created_at))
    ).all()
    
    return {
        "dailyStats": [
            {
                "date": r.date.strftime('%Y-%m-%d'),
                "count": r.count,
                "avgTime": round(r.avg_time, 2),
                "successRate": round((r.successes / r.count) * 100, 2) if r.count > 0 else 0
            }
            for r in daily_stats
        ],
        "timeRange": range
    }

@router.get("/usage")
async def get_usage_analytics(
    range: Literal["7d", "30d", "90d"] = Query(default="30d"),
    db: Session = Depends(get_db)
):
    """Usage patterns by hour and day"""
    days = {"7d": 7, "30d": 30, "90d": 90}[range]
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Hourly distribution
    hourly_dist = db.execute(
        select(
            extract('hour', GenerationLog.created_at).label('hour'),
            func.count(GenerationLog.id).label('count')
        )
        .where(GenerationLog.created_at >= cutoff)
        .group_by(extract('hour', GenerationLog.created_at))
        .order_by(extract('hour', GenerationLog.created_at))
    ).all()
    
    # Daily totals
    daily_totals = db.execute(
        select(
            func.date_trunc('day', GenerationLog.created_at).label('date'),
            func.count(GenerationLog.id).label('count')
        )
        .where(GenerationLog.created_at >= cutoff)
        .group_by(func.date_trunc('day', GenerationLog.created_at))
        .order_by(func.date_trunc('day', GenerationLog.created_at))
    ).all()
    
    return {
        "hourlyDistribution": [
            {"hour": int(r.hour), "count": r.count}
            for r in hourly_dist
        ],
        "dailyTotals": [
            {"date": r.date.strftime('%Y-%m-%d'), "count": r.count}
            for r in daily_totals
        ],
        "timeRange": range
    }