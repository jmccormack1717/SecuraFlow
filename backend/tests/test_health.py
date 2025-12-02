"""Tests for health check endpoints."""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "model_loaded" in data
    assert "uptime_seconds" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SecuraFlow API"
    assert "version" in data
    assert "status" in data


def test_health_check_database_status(client):
    """Test health check includes database status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert data["database"] in ["connected", "disconnected"]


def test_health_check_model_status(client):
    """Test health check includes model status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "model_loaded" in data
    assert isinstance(data["model_loaded"], bool)


def test_health_check_uptime(client):
    """Test health check includes uptime."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0



