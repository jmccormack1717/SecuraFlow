"""Traffic ingestion endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.base import get_db
from app.database.models import TrafficLog, Anomaly
from app.models.schemas import TrafficData, TrafficResponse
from app.services.feature_extractor import FeatureExtractor
from app.services.anomaly_detector import AnomalyDetector
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/traffic", tags=["traffic"])

# Initialize services (singleton pattern)
feature_extractor = FeatureExtractor()
anomaly_detector = AnomalyDetector()


@router.post("", response_model=TrafficResponse)
async def ingest_traffic(
    traffic_data: TrafficData,
    db: Session = Depends(get_db)
):
    """
    Ingest traffic data and detect anomalies.
    
    This endpoint receives traffic data, extracts features,
    runs anomaly detection, and stores the results.
    """
    try:
        # Set timestamp if not provided
        if not traffic_data.timestamp:
            traffic_data.timestamp = datetime.now()
        
        # Extract features
        features = feature_extractor.extract_features(traffic_data)
        
        # Run anomaly detection
        prediction = anomaly_detector.predict(features)
        
        # Store traffic log
        traffic_log = TrafficLog(
            timestamp=traffic_data.timestamp,
            endpoint=traffic_data.endpoint,
            method=traffic_data.method,
            status_code=traffic_data.status_code,
            response_time_ms=traffic_data.response_time_ms,
            request_size_bytes=traffic_data.request_size_bytes,
            response_size_bytes=traffic_data.response_size_bytes,
            ip_address=traffic_data.ip_address,
            user_agent=traffic_data.user_agent
        )
        db.add(traffic_log)
        db.flush()  # Get the ID
        
        # Store anomaly if detected
        if prediction["is_anomaly"]:
            anomaly = Anomaly(
                detected_at=traffic_data.timestamp,
                traffic_log_id=traffic_log.id,
                anomaly_score=prediction["anomaly_score"],
                anomaly_type=prediction["anomaly_type"],
                features=features,
                is_resolved=False
            )
            db.add(anomaly)
            logger.info(f"Anomaly detected: {prediction['anomaly_type']} (score: {prediction['anomaly_score']:.2f})")
        
        db.commit()
        
        return TrafficResponse(
            success=True,
            anomaly_detected=prediction["is_anomaly"],
            anomaly_score=prediction["anomaly_score"],
            message="Traffic data ingested successfully"
        )
    
    except Exception as e:
        logger.error(f"Error ingesting traffic data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing traffic data: {str(e)}")

