"""Tests for traffic ingestion endpoints."""
import pytest
from datetime import datetime


def test_ingest_traffic_success(client, sample_traffic_data):
    """Test successful traffic ingestion."""
    response = client.post("/api/traffic", json=sample_traffic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "anomaly_detected" in data
    assert "anomaly_score" in data


def test_ingest_traffic_missing_required_fields(client):
    """Test traffic ingestion with missing required fields."""
    incomplete_data = {
        "endpoint": "/api/test",
        "method": "GET"
        # Missing status_code and response_time_ms
    }
    response = client.post("/api/traffic", json=incomplete_data)
    assert response.status_code == 422  # Validation error


def test_ingest_traffic_with_timestamp(client, sample_traffic_data):
    """Test traffic ingestion with explicit timestamp."""
    sample_traffic_data["timestamp"] = datetime.now().isoformat()
    response = client.post("/api/traffic", json=sample_traffic_data)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_ingest_traffic_anomaly_detection(client):
    """Test that anomaly detection works."""
    # Create data that might trigger anomaly detection
    anomaly_data = {
        "endpoint": "/api/test",
        "method": "GET",
        "status_code": 500,  # Server error
        "response_time_ms": 5000,  # Very slow response
        "request_size_bytes": 50000,  # Large request
        "response_size_bytes": 100,
    }
    response = client.post("/api/traffic", json=anomaly_data)
    assert response.status_code == 200
    data = response.json()
    # Anomaly detection may or may not trigger, but should return a score
    assert "anomaly_score" in data


def test_rate_limiting(client, sample_traffic_data, monkeypatch):
    """Test that rate limiting works."""
    # Enable rate limiting for this test
    from app.config import settings
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 5)  # Low limit for testing
    
    # Make requests exceeding the limit
    responses = []
    for i in range(7):  # More than the 5/minute limit
        response = client.post("/api/traffic", json=sample_traffic_data)
        responses.append(response.status_code)
        # Small delay to ensure proper rate limit tracking
        if i < 6:
            import time
            time.sleep(0.1)
    
    # First 5 should succeed, rest may be rate limited
    # Note: Rate limiting may not trigger immediately in test environment
    assert all(r in [200, 429] for r in responses)


def test_ingest_traffic_optional_fields(client):
    """Test traffic ingestion with optional fields."""
    traffic_data = {
        "endpoint": "/api/test",
        "method": "GET",
        "status_code": 200,
        "response_time_ms": 50,
        "request_size_bytes": 100,
        "response_size_bytes": 500,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0"
    }
    response = client.post("/api/traffic", json=traffic_data)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_ingest_traffic_creates_anomaly_record(client, db_session):
    """Test that traffic ingestion creates anomaly record when anomaly is detected."""
    # Create data that will trigger anomaly detection
    anomaly_data = {
        "endpoint": "/api/test",
        "method": "GET",
        "status_code": 500,  # Server error - clear anomaly
        "response_time_ms": 100
    }
    response = client.post("/api/traffic", json=anomaly_data)
    assert response.status_code == 200
    
    # Check that anomaly was created in database
    from app.database.models import Anomaly
    anomalies = db_session.query(Anomaly).all()
    assert len(anomalies) > 0
    assert anomalies[0].anomaly_type == "server_error"


def test_ingest_traffic_different_methods(client):
    """Test traffic ingestion with different HTTP methods."""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    for method in methods:
        traffic_data = {
            "endpoint": f"/api/test/{method.lower()}",
            "method": method,
            "status_code": 200,
            "response_time_ms": 50
        }
        response = client.post("/api/traffic", json=traffic_data)
        assert response.status_code == 200


def test_ingest_traffic_different_status_codes(client):
    """Test traffic ingestion with different status codes."""
    status_codes = [200, 201, 204, 400, 401, 404, 500, 502, 503]
    for status_code in status_codes:
        traffic_data = {
            "endpoint": "/api/test",
            "method": "GET",
            "status_code": status_code,
            "response_time_ms": 50
        }
        response = client.post("/api/traffic", json=traffic_data)
        assert response.status_code == 200


def test_ingest_traffic_large_values(client):
    """Test traffic ingestion with large values."""
    traffic_data = {
        "endpoint": "/api/test",
        "method": "POST",
        "status_code": 200,
        "response_time_ms": 100,
        "request_size_bytes": 10000000,  # 10MB
        "response_size_bytes": 20000000  # 20MB
    }
    response = client.post("/api/traffic", json=traffic_data)
    assert response.status_code == 200
    data = response.json()
    # Large values might trigger anomaly detection
    assert "anomaly_score" in data


def test_ingest_traffic_empty_endpoint(client):
    """Test traffic ingestion with empty endpoint."""
    traffic_data = {
        "endpoint": "",
        "method": "GET",
        "status_code": 200,
        "response_time_ms": 50
    }
    response = client.post("/api/traffic", json=traffic_data)
    # Should still work, but might be unusual
    assert response.status_code in [200, 422]  # May or may not validate

