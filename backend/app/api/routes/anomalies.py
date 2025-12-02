"""Anomaly endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.base import get_db
from app.database.models import Anomaly, TrafficLog
from app.models.schemas import AnomaliesListResponse, AnomalyResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("", response_model=AnomaliesListResponse)
async def get_anomalies(
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of anomalies to return"),
    offset: int = Query(0, ge=0, description="Number of anomalies to skip"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db)
):
    """Get detected anomalies."""
    try:
        # Build query
        query = db.query(Anomaly)
        
        # Apply filters
        if resolved is not None:
            query = query.filter(Anomaly.is_resolved == resolved)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        anomalies = query.order_by(Anomaly.detected_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        anomaly_responses = []
        for anomaly in anomalies:
            # Get associated traffic log if available
            traffic_log_data = None
            if anomaly.traffic_log_id:
                traffic_log = db.query(TrafficLog).filter(TrafficLog.id == anomaly.traffic_log_id).first()
                if traffic_log:
                    traffic_log_data = {
                        "id": traffic_log.id,
                        "endpoint": traffic_log.endpoint,
                        "method": traffic_log.method,
                        "status_code": traffic_log.status_code,
                        "response_time_ms": traffic_log.response_time_ms,
                        "timestamp": traffic_log.timestamp.isoformat()
                    }
            
            anomaly_responses.append(
                AnomalyResponse(
                    id=anomaly.id,
                    detected_at=anomaly.detected_at,
                    anomaly_score=anomaly.anomaly_score,
                    anomaly_type=anomaly.anomaly_type,
                    features=anomaly.features,
                    is_resolved=anomaly.is_resolved,
                    traffic_log=traffic_log_data
                )
            )
        
        return AnomaliesListResponse(
            anomalies=anomaly_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching anomalies: {str(e)}")



