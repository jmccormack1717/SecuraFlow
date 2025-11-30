"""Tests for metrics endpoints."""
import pytest
from datetime import datetime, timedelta, timezone


def test_get_metrics_empty(client):
    """Test getting metrics when no data exists."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert isinstance(data["metrics"], list)


def test_get_metrics_with_data(client, sample_traffic_data):
    """Test getting metrics after ingesting traffic."""
    # Ingest some traffic first
    for _ in range(5):
        client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data["metrics"]) > 0


def test_get_metrics_with_time_range(client, sample_traffic_data):
    """Test getting metrics with time range."""
    # Ingest traffic
    client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics with time range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    
    response = client.get(
        "/api/metrics",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data


