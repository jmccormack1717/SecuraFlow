"""Tests for anomalies endpoints."""
import pytest


def test_get_anomalies_empty(client):
    """Test getting anomalies when none exist."""
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert "total" in data
    assert isinstance(data["anomalies"], list)


def test_get_anomalies_with_pagination(client):
    """Test anomalies endpoint with pagination."""
    response = client.get("/api/anomalies", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 10
    assert data["offset"] == 0


def test_get_anomalies_filter_unresolved(client):
    """Test filtering anomalies by resolved status."""
    response = client.get("/api/anomalies", params={"resolved": False})
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    # All returned anomalies should be unresolved
    for anomaly in data["anomalies"]:
        assert anomaly["is_resolved"] is False


def test_get_anomalies_filter_resolved(client, db_session):
    """Test filtering anomalies by resolved status (resolved=True)."""
    from app.database.models import Anomaly, TrafficLog
    from datetime import datetime, timezone
    
    # Create a resolved anomaly
    traffic_log = TrafficLog(
        timestamp=datetime.now(timezone.utc),
        endpoint="/api/test",
        method="GET",
        status_code=500,
        response_time_ms=100
    )
    db_session.add(traffic_log)
    db_session.flush()
    
    anomaly = Anomaly(
        detected_at=datetime.now(timezone.utc),
        traffic_log_id=traffic_log.id,
        anomaly_score=0.9,
        anomaly_type="server_error",
        is_resolved=True
    )
    db_session.add(anomaly)
    db_session.commit()
    
    # Get resolved anomalies
    response = client.get("/api/anomalies", params={"resolved": True})
    assert response.status_code == 200
    data = response.json()
    for anomaly in data["anomalies"]:
        assert anomaly["is_resolved"] is True


def test_get_anomalies_pagination(client, db_session):
    """Test anomalies endpoint pagination."""
    from app.database.models import Anomaly, TrafficLog
    from datetime import datetime, timezone
    
    # Create multiple anomalies
    for i in range(15):
        traffic_log = TrafficLog(
            timestamp=datetime.now(timezone.utc),
            endpoint=f"/api/test{i}",
            method="GET",
            status_code=500,
            response_time_ms=100
        )
        db_session.add(traffic_log)
        db_session.flush()
        
        anomaly = Anomaly(
            detected_at=datetime.now(timezone.utc),
            traffic_log_id=traffic_log.id,
            anomaly_score=0.9,
            anomaly_type="server_error",
            is_resolved=False
        )
        db_session.add(anomaly)
    db_session.commit()
    
    # Get first page
    response = client.get("/api/anomalies", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert len(data["anomalies"]) == 10
    assert data["limit"] == 10
    assert data["offset"] == 0
    
    # Get second page
    response = client.get("/api/anomalies", params={"limit": 10, "offset": 10})
    assert response.status_code == 200
    data = response.json()
    assert len(data["anomalies"]) == 5  # Remaining 5


def test_get_anomalies_includes_traffic_log(client, db_session):
    """Test that anomalies response includes associated traffic log."""
    from app.database.models import Anomaly, TrafficLog
    from datetime import datetime, timezone
    
    # Create anomaly with traffic log
    traffic_log = TrafficLog(
        timestamp=datetime.now(timezone.utc),
        endpoint="/api/test",
        method="GET",
        status_code=500,
        response_time_ms=100
    )
    db_session.add(traffic_log)
    db_session.flush()
    
    anomaly = Anomaly(
        detected_at=datetime.now(timezone.utc),
        traffic_log_id=traffic_log.id,
        anomaly_score=0.9,
        anomaly_type="server_error",
        is_resolved=False
    )
    db_session.add(anomaly)
    db_session.commit()
    
    # Get anomalies
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["anomalies"]) > 0:
        anomaly_data = data["anomalies"][0]
        assert "traffic_log" in anomaly_data
        if anomaly_data["traffic_log"]:
            assert "endpoint" in anomaly_data["traffic_log"]
            assert "method" in anomaly_data["traffic_log"]
            assert "status_code" in anomaly_data["traffic_log"]


def test_get_anomalies_ordering(client, db_session):
    """Test that anomalies are returned in descending order by detection time."""
    from app.database.models import Anomaly, TrafficLog
    from datetime import datetime, timezone, timedelta
    
    # Create anomalies with different timestamps
    base_time = datetime.now(timezone.utc)
    for i in range(5):
        traffic_log = TrafficLog(
            timestamp=base_time - timedelta(minutes=i),
            endpoint=f"/api/test{i}",
            method="GET",
            status_code=500,
            response_time_ms=100
        )
        db_session.add(traffic_log)
        db_session.flush()
        
        anomaly = Anomaly(
            detected_at=base_time - timedelta(minutes=i),
            traffic_log_id=traffic_log.id,
            anomaly_score=0.9,
            anomaly_type="server_error",
            is_resolved=False
        )
        db_session.add(anomaly)
    db_session.commit()
    
    # Get anomalies
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    
    # Check ordering (most recent first)
    if len(data["anomalies"]) > 1:
        dates = [a["detected_at"] for a in data["anomalies"]]
        assert dates == sorted(dates, reverse=True)


def test_get_anomalies_max_limit(client):
    """Test anomalies endpoint with maximum limit."""
    response = client.get("/api/anomalies", params={"limit": 1000})
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 1000


def test_get_anomalies_invalid_limit(client):
    """Test anomalies endpoint with invalid limit."""
    # Limit too high
    response = client.get("/api/anomalies", params={"limit": 2000})
    assert response.status_code == 422  # Validation error
    
    # Limit too low
    response = client.get("/api/anomalies", params={"limit": 0})
    assert response.status_code == 422  # Validation error



