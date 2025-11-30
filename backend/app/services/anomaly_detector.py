"""ML-based anomaly detection service."""
import pickle
import os
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    """Anomaly detection using ML model."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self) -> bool:
        """Load the trained ML model and scaler."""
        try:
            model_path = settings.model_path
            model_dir = os.path.dirname(model_path) if os.path.dirname(model_path) else "."
            scaler_path = os.path.join(model_dir, "scaler_v1.pkl")
            
            # Handle relative paths
            if not os.path.isabs(model_path):
                model_path = os.path.join(os.getcwd(), model_path)
            if not os.path.isabs(scaler_path):
                scaler_path = os.path.join(os.getcwd(), scaler_path)
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.model_loaded = True
                logger.info(f"Model and scaler loaded successfully")
                return True
            else:
                logger.warning(f"Model files not found at {model_path} or {scaler_path}. Using fallback detection.")
                self.model_loaded = False
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict anomaly score for given features.
        
        Args:
            features: Dictionary of feature values
        
        Returns:
            Dictionary with anomaly_score, is_anomaly, and anomaly_type
        """
        if not self.model_loaded or self.model is None:
            # Fallback to simple statistical detection
            return self._statistical_detection(features)
        
        try:
            # Convert features dict to array (model expects specific order)
            feature_array = self._features_to_array(features)
            
            # Scale features using the trained scaler
            if self.scaler:
                feature_array_scaled = self.scaler.transform([feature_array])[0]
            else:
                feature_array_scaled = feature_array
            
            # Get anomaly score from Isolation Forest
            # decision_function returns: negative for anomalies, positive for normal
            # Typical range: -0.5 (most anomalous) to 0.5 (most normal)
            raw_score = self.model.decision_function([feature_array_scaled])[0]
            
            # FIXED: Convert to 0-1 range where higher = more anomalous
            # Isolation Forest: negative = anomaly, positive = normal
            # We want: -0.5 (most anomalous) -> 1.0, 0.5 (most normal) -> 0.0
            if raw_score < 0:
                # It's an anomaly: more negative = higher score
                # -0.5 -> 1.0, -0.1 -> 0.8
                normalized_score = 1.0 - (abs(raw_score) * 2)
            else:
                # It's normal: more positive = lower score
                # 0.0 -> 0.5, 0.5 -> 0.0
                normalized_score = max(0.0, 0.5 - (raw_score * 1.0))
            
            # Ensure score is in [0, 1] range
            normalized_score = max(0.0, min(1.0, normalized_score))
            
            # Use threshold to determine if it's an anomaly
            # Higher threshold = fewer false positives, better precision
            is_anomaly = normalized_score >= settings.anomaly_threshold
            
            # Determine anomaly type
            anomaly_type = self._classify_anomaly_type(features, normalized_score)
            
            return {
                "anomaly_score": float(normalized_score),
                "is_anomaly": is_anomaly,
                "anomaly_type": anomaly_type
            }
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            return self._statistical_detection(features)
    
    def _features_to_array(self, features: Dict[str, float]) -> list:
        """Convert features dict to array in model's expected order."""
        # Feature order must match training script
        feature_order = [
            "response_time_ms",
            "status_code",
            "request_size_bytes",
            "response_size_bytes",
            "hour_of_day",
            "day_of_week",
            "minute_of_hour",
            "is_error",
            "is_server_error",
            "is_client_error",
            "endpoint_length",
            "method_get",
            "method_post",
            "response_to_request_ratio",
            "throughput_mbps",
            "is_very_slow",
            "is_very_large_request",
            "is_very_large_response",
        ]
        
        return [features.get(key, 0.0) for key in feature_order]
    
    def _statistical_detection(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Fallback statistical anomaly detection - matches demo data patterns."""
        score = 0.0
        anomaly_type = "normal"
        
        # Check for server errors (5xx) - highest priority, clear anomaly
        if features.get("is_server_error", 0) > 0:
            score = 0.9  # High score for server errors
            anomaly_type = "server_error"
        # Check for very slow responses (>3000ms) - matches demo data
        elif features.get("response_time_ms", 0) > 3000:
            score = 0.85  # High score for very slow
            anomaly_type = "response_time_spike"
        # Check for very large requests (>10MB) - matches demo data
        elif features.get("request_size_bytes", 0) > 10000000:
            score = 0.8  # High score for very large requests
            anomaly_type = "large_request"
        # Check for very large responses (>10MB) - matches demo data
        elif features.get("response_size_bytes", 0) > 10000000:
            score = 0.8  # High score for very large responses
            anomaly_type = "large_response"
        # Check for moderately slow responses (>1000ms)
        elif features.get("response_time_ms", 0) > 1000:
            score = 0.5
            anomaly_type = "response_time_spike"
        # Check for client errors (4xx)
        elif features.get("is_client_error", 0) > 0:
            score = 0.3
            anomaly_type = "client_error"
        
        return {
            "anomaly_score": min(score, 1.0),
            "is_anomaly": score >= settings.anomaly_threshold,
            "anomaly_type": anomaly_type
        }
    
    def _classify_anomaly_type(self, features: Dict[str, float], score: float) -> str:
        """Classify the type of anomaly based on features."""
        if features.get("is_server_error", 0) > 0:
            return "server_error"
        elif features.get("is_client_error", 0) > 0:
            return "client_error"
        elif features.get("response_time_ms", 0) > 1000:
            return "response_time_spike"
        elif features.get("request_size_bytes", 0) > 1000000:
            return "large_request"
        elif score >= settings.anomaly_threshold:
            return "pattern_anomaly"
        else:
            return "normal"

