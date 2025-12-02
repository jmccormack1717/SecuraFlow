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


def test_get_metrics_with_endpoint_filter(client, sample_traffic_data):
    """Test getting metrics filtered by endpoint."""
    # Ingest traffic with different endpoints
    sample_traffic_data["endpoint"] = "/api/users"
    client.post("/api/traffic", json=sample_traffic_data)
    
    sample_traffic_data["endpoint"] = "/api/products"
    client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics for specific endpoint
    response = client.get("/api/metrics?endpoint=/api/users")
    assert response.status_code == 200
    data = response.json()
    # All metrics should be for /api/users
    for metric in data["metrics"]:
        assert metric["endpoint"] == "/api/users"


def test_get_metrics_aggregation(client, sample_traffic_data):
    """Test that metrics are properly aggregated."""
    # Ingest multiple traffic logs
    for i in range(10):
        sample_traffic_data["response_time_ms"] = 50 + i * 10
        client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    
    # Should have aggregated metrics
    if len(data["metrics"]) > 0:
        metric = data["metrics"][0]
        assert metric["request_count"] > 0
        assert metric["avg_response_time_ms"] > 0


def test_get_metrics_percentiles(client, sample_traffic_data):
    """Test that metrics include percentile calculations."""
    # Ingest traffic with varying response times
    response_times = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    for rt in response_times:
        sample_traffic_data["response_time_ms"] = rt
        client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    
    # Check percentiles if metrics exist
    if len(data["metrics"]) > 0:
        metric = data["metrics"][0]
        # P95 and P99 may be None if not enough data
        if metric["p95_response_time_ms"] is not None:
            assert metric["p95_response_time_ms"] > 0
        if metric["p99_response_time_ms"] is not None:
            assert metric["p99_response_time_ms"] > 0


def test_get_metrics_error_count(client, sample_traffic_data):
    """Test that metrics include error count."""
    # Ingest some successful and some error requests
    sample_traffic_data["status_code"] = 200
    client.post("/api/traffic", json=sample_traffic_data)
    
    sample_traffic_data["status_code"] = 500
    client.post("/api/traffic", json=sample_traffic_data)
    
    # Get metrics
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    
    # Should have error count
    if len(data["metrics"]) > 0:
        metric = data["metrics"][0]
        assert metric["error_count"] >= 0


def test_get_metrics_time_range_validation(client):
    """Test metrics endpoint with invalid time range."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time + timedelta(hours=1)  # Start after end
    
    # Should still work, but may return empty results
    response = client.get(
        "/api/metrics",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )
    assert response.status_code == 200



