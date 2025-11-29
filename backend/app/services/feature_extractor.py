"""Feature extraction service for traffic data."""
from typing import Dict, Any
from datetime import datetime
from app.models.schemas import TrafficData


class FeatureExtractor:
    """Extract features from traffic data for ML model."""
    
    @staticmethod
    def extract_features(traffic_data: TrafficData, context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Extract features from traffic data.
        
        Args:
            traffic_data: Traffic data to extract features from
            context: Additional context (e.g., recent metrics)
        
        Returns:
            Dictionary of feature names and values
        """
        timestamp = traffic_data.timestamp or datetime.now()
        
        features = {
            # Basic features
            "response_time_ms": float(traffic_data.response_time_ms),
            "status_code": float(traffic_data.status_code),
            "request_size_bytes": float(traffic_data.request_size_bytes or 0),
            "response_size_bytes": float(traffic_data.response_size_bytes or 0),
            
            # Time-based features
            "hour_of_day": float(timestamp.hour),
            "day_of_week": float(timestamp.weekday()),
            "minute_of_hour": float(timestamp.minute),
            
            # Status code features
            "is_error": 1.0 if traffic_data.status_code >= 400 else 0.0,
            "is_server_error": 1.0 if traffic_data.status_code >= 500 else 0.0,
            "is_client_error": 1.0 if 400 <= traffic_data.status_code < 500 else 0.0,
            
            # Endpoint features (simple hash for now)
            "endpoint_length": float(len(traffic_data.endpoint)),
            "method_get": 1.0 if traffic_data.method.upper() == "GET" else 0.0,
            "method_post": 1.0 if traffic_data.method.upper() == "POST" else 0.0,
        }
        
        # Add context features if available
        if context:
            features.update({
                "recent_avg_response_time": context.get("recent_avg_response_time", 0.0),
                "recent_error_rate": context.get("recent_error_rate", 0.0),
                "recent_request_rate": context.get("recent_request_rate", 0.0),
            })
        
        return features

