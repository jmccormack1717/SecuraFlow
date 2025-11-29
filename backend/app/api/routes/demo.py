"""Demo data generation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import random
from app.database.base import get_db
from app.database.models import TrafficLog, Anomaly
from app.models.schemas import TrafficData
from app.services.feature_extractor import FeatureExtractor
from app.services.anomaly_detector import AnomalyDetector
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/demo", tags=["demo"])

# Initialize services
feature_extractor = FeatureExtractor()
anomaly_detector = AnomalyDetector()

# Common endpoints and methods
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/search",
    "/api/analytics",
    "/api/notifications",
]

METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
]


def generate_normal_traffic_data(timestamp: datetime) -> dict:
    """Generate normal traffic data."""
    return {
        "endpoint": random.choice(ENDPOINTS),
        "method": random.choice(METHODS),
        "status_code": random.choices(
            [200, 201, 204],
            weights=[80, 15, 5]
        )[0],
        "response_time_ms": random.randint(50, 300),
        "request_size_bytes": random.randint(100, 2000),
        "response_size_bytes": random.randint(500, 5000),
        "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        "user_agent": random.choice(USER_AGENTS),
        "timestamp": timestamp,
    }


def generate_anomaly_traffic_data(timestamp: datetime) -> dict:
    """Generate anomaly traffic data."""
    anomaly_type = random.choice([
        "server_error",
        "client_error",
        "response_time_spike",
        "large_request",
    ])
    
    if anomaly_type == "server_error":
        return {
            "endpoint": random.choice(ENDPOINTS),
            "method": random.choice(METHODS),
            "status_code": random.choice([500, 502, 503, 504]),
            "response_time_ms": random.randint(1000, 5000),
            "request_size_bytes": random.randint(100, 2000),
            "response_size_bytes": random.randint(100, 500),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user_agent": random.choice(USER_AGENTS),
            "timestamp": timestamp,
        }
    elif anomaly_type == "client_error":
        return {
            "endpoint": random.choice(ENDPOINTS),
            "method": random.choice(METHODS),
            "status_code": random.choice([400, 401, 403, 404]),
            "response_time_ms": random.randint(50, 200),
            "request_size_bytes": random.randint(100, 2000),
            "response_size_bytes": random.randint(100, 500),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user_agent": random.choice(USER_AGENTS),
            "timestamp": timestamp,
        }
    elif anomaly_type == "response_time_spike":
        return {
            "endpoint": random.choice(ENDPOINTS),
            "method": random.choice(METHODS),
            "status_code": 200,
            "response_time_ms": random.randint(2000, 10000),
            "request_size_bytes": random.randint(100, 2000),
            "response_size_bytes": random.randint(500, 5000),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user_agent": random.choice(USER_AGENTS),
            "timestamp": timestamp,
        }
    else:  # large_request
        return {
            "endpoint": random.choice(ENDPOINTS),
            "method": random.choice(METHODS),
            "status_code": 200,
            "response_time_ms": random.randint(100, 500),
            "request_size_bytes": random.randint(10000, 50000),
            "response_size_bytes": random.randint(50000, 200000),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user_agent": random.choice(USER_AGENTS),
            "timestamp": timestamp,
        }


@router.post("/generate")
async def generate_demo_data(
    count: int = Query(100, ge=1, le=1000, description="Number of traffic logs to generate"),
    anomaly_rate: float = Query(0.15, ge=0.0, le=1.0, description="Percentage of anomalies (0.0 to 1.0)"),
    hours_back: int = Query(24, ge=1, le=168, description="Generate data for the last N hours"),
    db: Session = Depends(get_db)
):
    """
    Generate demo traffic data for testing and demonstration.
    
    This endpoint creates synthetic traffic logs with optional anomalies
    distributed over the specified time period.
    """
    try:
        logger.info(f"Generating {count} demo traffic logs with {anomaly_rate * 100}% anomaly rate")
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        # Generate timestamps distributed over the time range
        timestamps = []
        for i in range(count):
            # Distribute timestamps evenly over the time range
            time_offset = (i / count) * hours_back
            timestamp = start_time + timedelta(hours=time_offset)
            timestamps.append(timestamp)
        
        # Shuffle timestamps for more realistic distribution
        random.shuffle(timestamps)
        
        traffic_logs_created = 0
        anomalies_created = 0
        
        for timestamp in timestamps:
            try:
                # Generate normal or anomaly traffic
                if random.random() < anomaly_rate:
                    traffic_data_dict = generate_anomaly_traffic_data(timestamp)
                else:
                    traffic_data_dict = generate_normal_traffic_data(timestamp)
                
                # Create TrafficData object
                traffic_data = TrafficData(**traffic_data_dict)
                
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
                    anomalies_created += 1
                
                traffic_logs_created += 1
                
            except Exception as e:
                logger.error(f"Error generating traffic log: {e}")
                continue
        
        # Commit all at once
        db.commit()
        
        logger.info(f"Generated {traffic_logs_created} traffic logs with {anomalies_created} anomalies")
        
        return {
            "success": True,
            "message": f"Generated {traffic_logs_created} traffic logs",
            "traffic_logs_created": traffic_logs_created,
            "anomalies_created": anomalies_created,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating demo data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating demo data: {str(e)}")

