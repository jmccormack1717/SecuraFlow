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

