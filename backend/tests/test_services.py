"""Tests for service layer (anomaly detector, feature extractor)."""
import pytest
from datetime import datetime
from app.services.feature_extractor import FeatureExtractor
from app.services.anomaly_detector import AnomalyDetector
from app.models.schemas import TrafficData


def test_feature_extractor_basic_features():
    """Test feature extraction with basic traffic data."""
    extractor = FeatureExtractor()
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=50,
        request_size_bytes=100,
        response_size_bytes=500
    )
    
    features = extractor.extract_features(traffic_data)
    
    # Check basic features
    assert features["response_time_ms"] == 50.0
    assert features["status_code"] == 200.0
    assert features["request_size_bytes"] == 100.0
    assert features["response_size_bytes"] == 500.0
    assert features["is_error"] == 0.0
    assert features["is_server_error"] == 0.0
    assert features["is_client_error"] == 0.0


def test_feature_extractor_error_detection():
    """Test feature extraction correctly identifies errors."""
    extractor = FeatureExtractor()
    
    # Server error
    server_error_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=500,
        response_time_ms=100
    )
    features = extractor.extract_features(server_error_data)
    assert features["is_error"] == 1.0
    assert features["is_server_error"] == 1.0
    assert features["is_client_error"] == 0.0
    
    # Client error
    client_error_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=404,
        response_time_ms=50
    )
    features = extractor.extract_features(client_error_data)
    assert features["is_error"] == 1.0
    assert features["is_server_error"] == 0.0
    assert features["is_client_error"] == 1.0


def test_feature_extractor_method_features():
    """Test feature extraction for HTTP methods."""
    extractor = FeatureExtractor()
    
    # GET request
    get_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=50
    )
    features = extractor.extract_features(get_data)
    assert features["method_get"] == 1.0
    assert features["method_post"] == 0.0
    
    # POST request
    post_data = TrafficData(
        endpoint="/api/test",
        method="POST",
        status_code=201,
        response_time_ms=100
    )
    features = extractor.extract_features(post_data)
    assert features["method_get"] == 0.0
    assert features["method_post"] == 1.0


def test_feature_extractor_derived_features():
    """Test feature extraction calculates derived features correctly."""
    extractor = FeatureExtractor()
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=100,
        request_size_bytes=1000,
        response_size_bytes=5000
    )
    
    features = extractor.extract_features(traffic_data)
    
    # Check derived features
    assert "response_to_request_ratio" in features
    assert features["response_to_request_ratio"] == 5.0  # 5000 / 1000
    
    assert "throughput_mbps" in features
    assert features["throughput_mbps"] > 0
    
    assert "is_very_slow" in features
    assert features["is_very_slow"] == 0.0  # 100ms is not very slow
    
    assert "is_very_large_request" in features
    assert "is_very_large_response" in features


def test_feature_extractor_time_features():
    """Test feature extraction includes time-based features."""
    extractor = FeatureExtractor()
    timestamp = datetime(2024, 1, 15, 14, 30, 0)  # Monday, 2:30 PM
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=50,
        timestamp=timestamp
    )
    
    features = extractor.extract_features(traffic_data)
    
    assert "hour_of_day" in features
    assert features["hour_of_day"] == 14.0
    
    assert "day_of_week" in features
    assert features["day_of_week"] == 0.0  # Monday
    
    assert "minute_of_hour" in features
    assert features["minute_of_hour"] == 30.0


def test_anomaly_detector_initialization():
    """Test anomaly detector initializes correctly."""
    detector = AnomalyDetector()
    assert detector is not None
    # Model may or may not be loaded depending on test environment
    assert hasattr(detector, "model_loaded")


def test_anomaly_detector_predict_normal_traffic():
    """Test anomaly detector on normal traffic."""
    detector = AnomalyDetector()
    extractor = FeatureExtractor()
    
    # Normal traffic
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=50,
        request_size_bytes=100,
        response_size_bytes=500
    )
    
    features = extractor.extract_features(traffic_data)
    prediction = detector.predict(features)
    
    assert "anomaly_score" in prediction
    assert "is_anomaly" in prediction
    assert "anomaly_type" in prediction
    assert 0 <= prediction["anomaly_score"] <= 1


def test_anomaly_detector_predict_server_error():
    """Test anomaly detector on server error."""
    detector = AnomalyDetector()
    extractor = FeatureExtractor()
    
    # Server error - should be detected as anomaly
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=500,
        response_time_ms=100
    )
    
    features = extractor.extract_features(traffic_data)
    prediction = detector.predict(features)
    
    assert prediction["is_anomaly"] is True
    assert prediction["anomaly_type"] == "server_error"
    assert prediction["anomaly_score"] > 0.5


def test_anomaly_detector_predict_very_slow():
    """Test anomaly detector on very slow response."""
    detector = AnomalyDetector()
    extractor = FeatureExtractor()
    
    # Very slow response - should be detected as anomaly
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        response_time_ms=5000  # 5 seconds
    )
    
    features = extractor.extract_features(traffic_data)
    prediction = detector.predict(features)
    
    assert prediction["is_anomaly"] is True
    assert prediction["anomaly_type"] == "response_time_spike"
    assert prediction["anomaly_score"] > 0.5


def test_anomaly_detector_predict_very_large():
    """Test anomaly detector on very large request/response."""
    detector = AnomalyDetector()
    extractor = FeatureExtractor()
    
    # Very large request - should be detected as anomaly
    traffic_data = TrafficData(
        endpoint="/api/test",
        method="POST",
        status_code=200,
        response_time_ms=100,
        request_size_bytes=15000000,  # 15MB
        response_size_bytes=20000000  # 20MB
    )
    
    features = extractor.extract_features(traffic_data)
    prediction = detector.predict(features)
    
    assert prediction["is_anomaly"] is True
    assert prediction["anomaly_score"] > 0.5


def test_anomaly_detector_classify_anomaly_types():
    """Test anomaly detector classifies different anomaly types."""
    detector = AnomalyDetector()
    extractor = FeatureExtractor()
    
    # Test different anomaly types
    test_cases = [
        (500, 100, None, None, "server_error"),
        (200, 5000, None, None, "response_time_spike"),
        (200, 100, 15000000, None, "large_request"),
    ]
    
    for status, response_time, req_size, resp_size, expected_type in test_cases:
        traffic_data = TrafficData(
            endpoint="/api/test",
            method="GET",
            status_code=status,
            response_time_ms=response_time,
            request_size_bytes=req_size,
            response_size_bytes=resp_size
        )
        
        features = extractor.extract_features(traffic_data)
        prediction = detector.predict(features)
        
        if prediction["is_anomaly"]:
            assert prediction["anomaly_type"] in [expected_type, "pattern_anomaly"]

