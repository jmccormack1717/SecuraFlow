"""Metrics endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
from app.database.base import get_db
from app.database.models import Metric, TrafficLog
from app.models.schemas import MetricsListResponse, MetricResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("", response_model=MetricsListResponse)
async def get_metrics(
    start_time: Optional[datetime] = Query(None, description="Start time for metrics"),
    end_time: Optional[datetime] = Query(None, description="End time for metrics"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics.
    
    If no time range is provided, returns metrics from the last hour.
    """
    try:
        # Default to last hour if no time range provided
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(hours=1)
        
        # Build query
        query = db.query(Metric)
        
        # Apply filters
        if start_time:
            query = query.filter(Metric.time_window >= start_time)
        if end_time:
            query = query.filter(Metric.time_window <= end_time)
        if endpoint:
            query = query.filter(Metric.endpoint == endpoint)
        
        # Order by time
        query = query.order_by(Metric.time_window.desc())
        
        # Execute query
        metrics = query.all()
        
        # Convert to response format
        metric_responses = [
            MetricResponse(
                time_window=metric.time_window,
                endpoint=metric.endpoint,
                request_count=metric.request_count,
                avg_response_time_ms=metric.avg_response_time_ms,
                error_count=metric.error_count,
                p95_response_time_ms=metric.p95_response_time_ms,
                p99_response_time_ms=metric.p99_response_time_ms
            )
            for metric in metrics
        ]
        
        return MetricsListResponse(
            metrics=metric_responses,
            total=len(metric_responses)
        )
    
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")

