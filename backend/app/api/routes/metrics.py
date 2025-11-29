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
    Aggregates directly from traffic logs.
    """
    try:
        # Default to last hour if no time range provided
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(hours=1)
        
        # Query traffic logs
        query = db.query(TrafficLog).filter(
            TrafficLog.timestamp >= start_time,
            TrafficLog.timestamp <= end_time
        )
        
        if endpoint:
            query = query.filter(TrafficLog.endpoint == endpoint)
        
        traffic_logs = query.all()
        
        # If no logs, return empty
        if not traffic_logs:
            return MetricsListResponse(metrics=[], total=0)
        
        # Aggregate by time window (1 minute windows)
        metrics_dict = {}
        
        for log in traffic_logs:
            # Round timestamp to nearest minute for grouping
            time_window = log.timestamp.replace(second=0, microsecond=0)
            key = (time_window, log.endpoint if not endpoint else None)
            
            if key not in metrics_dict:
                metrics_dict[key] = {
                    'time_window': time_window,
                    'endpoint': log.endpoint if not endpoint else None,
                    'response_times': [],
                    'error_count': 0,
                    'request_count': 0
                }
            
            metrics_dict[key]['request_count'] += 1
            metrics_dict[key]['response_times'].append(log.response_time_ms)
            
            if log.status_code >= 400:
                metrics_dict[key]['error_count'] += 1
        
        # Convert to response format and calculate percentiles
        metric_responses = []
        for key, data in sorted(metrics_dict.items(), key=lambda x: x[1]['time_window'], reverse=True):
            response_times = data['response_times']
            sorted_times = sorted(response_times)
            
            p95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else None
            p99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else None
            
            metric_responses.append(
                MetricResponse(
                    time_window=data['time_window'],
                    endpoint=data['endpoint'],
                    request_count=data['request_count'],
                    avg_response_time_ms=sum(response_times) / len(response_times) if response_times else 0,
                    error_count=data['error_count'],
                    p95_response_time_ms=p95,
                    p99_response_time_ms=p99
                )
            )
        
        return MetricsListResponse(
            metrics=metric_responses,
            total=len(metric_responses)
        )
    
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")

