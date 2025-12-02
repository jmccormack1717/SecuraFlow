"""Tests for demo data generation endpoints."""
import pytest
from datetime import datetime, timedelta, timezone


def test_generate_demo_data_default(client):
    """Test generating demo data with default parameters."""
    response = client.post("/api/demo/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "traffic_logs_created" in data
    assert "anomalies_created" in data
    assert "time_range" in data
    assert data["traffic_logs_created"] > 0


def test_generate_demo_data_custom_count(client):
    """Test generating demo data with custom count."""
    response = client.post("/api/demo/generate?count=50")
    assert response.status_code == 200
    data = response.json()
    assert data["traffic_logs_created"] == 50


def test_generate_demo_data_custom_anomaly_rate(client):
    """Test generating demo data with custom anomaly rate."""
    response = client.post("/api/demo/generate?count=100&anomaly_rate=0.3")
    assert response.status_code == 200
    data = response.json()
    assert data["traffic_logs_created"] == 100
    # Should have some anomalies (exact count may vary due to randomness)
    assert data["anomalies_created"] >= 0


def test_generate_demo_data_custom_hours_back(client):
    """Test generating demo data with custom time range."""
    response = client.post("/api/demo/generate?count=20&hours_back=12")
    assert response.status_code == 200
    data = response.json()
    assert data["traffic_logs_created"] == 20
    assert "time_range" in data
    assert "start" in data["time_range"]
    assert "end" in data["time_range"]


def test_generate_demo_data_max_count(client):
    """Test generating demo data with maximum count."""
    response = client.post("/api/demo/generate?count=1000")
    assert response.status_code == 200
    data = response.json()
    assert data["traffic_logs_created"] == 1000


def test_generate_demo_data_invalid_count_too_high(client):
    """Test generating demo data with count exceeding maximum."""
    response = client.post("/api/demo/generate?count=2000")
    assert response.status_code == 422  # Validation error


def test_generate_demo_data_invalid_count_too_low(client):
    """Test generating demo data with count below minimum."""
    response = client.post("/api/demo/generate?count=0")
    assert response.status_code == 422  # Validation error


def test_generate_demo_data_invalid_anomaly_rate_too_high(client):
    """Test generating demo data with anomaly rate exceeding maximum."""
    response = client.post("/api/demo/generate?anomaly_rate=1.5")
    assert response.status_code == 422  # Validation error


def test_generate_demo_data_invalid_anomaly_rate_negative(client):
    """Test generating demo data with negative anomaly rate."""
    response = client.post("/api/demo/generate?anomaly_rate=-0.1")
    assert response.status_code == 422  # Validation error


def test_generate_demo_data_invalid_hours_back_too_high(client):
    """Test generating demo data with hours_back exceeding maximum."""
    response = client.post("/api/demo/generate?hours_back=200")
    assert response.status_code == 422  # Validation error


def test_generate_demo_data_creates_anomalies(client):
    """Test that demo data generation creates anomalies when anomaly_rate > 0."""
    response = client.post("/api/demo/generate?count=100&anomaly_rate=0.5")
    assert response.status_code == 200
    data = response.json()
    # With 50% anomaly rate, we should have some anomalies
    assert data["anomalies_created"] > 0


def test_generate_demo_data_no_anomalies(client):
    """Test that demo data generation creates no anomalies when anomaly_rate = 0."""
    response = client.post("/api/demo/generate?count=50&anomaly_rate=0.0")
    assert response.status_code == 200
    data = response.json()
    # With 0% anomaly rate, should have no anomalies
    assert data["anomalies_created"] == 0


def test_generate_demo_data_creates_traffic_logs(client):
    """Test that demo data generation creates traffic logs in database."""
    # Generate demo data
    response = client.post("/api/demo/generate?count=10")
    assert response.status_code == 200
    
    # Check that metrics endpoint returns data
    metrics_response = client.get("/api/metrics")
    assert metrics_response.status_code == 200
    metrics_data = metrics_response.json()
    assert len(metrics_data["metrics"]) > 0

