"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
from app.database.base import get_db
from app.models.schemas import HealthResponse
from app.services.anomaly_detector import AnomalyDetector
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])

# Track startup time for uptime calculation
startup_time = time.time()
anomaly_detector = AnomalyDetector()


@router.get("", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        db_status = "connected"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"disconnected: {str(e)}"
            logger.error(f"Database health check failed: {e}")
        
        # Check model status
        model_loaded = anomaly_detector.model_loaded
        
        # Calculate uptime
        uptime_seconds = time.time() - startup_time
        
        status = "healthy" if db_status == "connected" and model_loaded else "degraded"
        
        return HealthResponse(
            status=status,
            database=db_status,
            model_loaded=model_loaded,
            uptime_seconds=uptime_seconds
        )
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            database="unknown",
            model_loaded=False,
            uptime_seconds=0.0
        )

