"""Tests for model metrics endpoints."""
import pytest
from datetime import datetime, timezone


def test_get_model_metrics_empty(client):
    """Test getting model metrics when none exist."""
    response = client.get("/api/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert isinstance(data["metrics"], list)
    assert len(data["metrics"]) == 0


def test_get_model_metrics_with_limit(client, db_session):
    """Test getting model metrics with limit."""
    from app.database.models import ModelPerformance
    
    # Create some model performance records
    for i in range(5):
        perf = ModelPerformance(
            model_version="v1",
            evaluation_date=datetime.now(timezone.utc),
            total_predictions=100,
            true_positives=10,
            false_positives=5,
            true_negatives=80,
            false_negatives=5,
            precision=0.67,
            recall=0.67,
            f1_score=0.67,
            accuracy=0.90,
            avg_anomaly_score=0.75,
            threshold_used=0.6
        )
        db_session.add(perf)
    db_session.commit()
    
    # Get metrics with limit
    response = client.get("/api/model-metrics?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["metrics"]) == 3
    assert data["total"] == 3


def test_evaluate_model_performance_no_data(client):
    """Test evaluating model performance when no traffic logs exist."""
    response = client.post("/api/model-metrics/evaluate")
    assert response.status_code == 404
    assert "no traffic logs found" in response.json()["detail"].lower()


def test_evaluate_model_performance_with_data(client):
    """Test evaluating model performance with existing traffic data."""
    # First, generate some demo data
    demo_response = client.post("/api/demo/generate?count=100&anomaly_rate=0.2")
    assert demo_response.status_code == 200
    
    # Evaluate model performance
    response = client.post("/api/model-metrics/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "total_predictions" in data
    assert "precision" in data
    assert "recall" in data
    assert "f1_score" in data
    assert "accuracy" in data
    assert "threshold_used" in data
    assert data["total_predictions"] > 0


def test_evaluate_model_performance_with_custom_limit(client):
    """Test evaluating model performance with custom limit."""
    # Generate demo data
    client.post("/api/demo/generate?count=200&anomaly_rate=0.15")
    
    # Evaluate with custom limit
    response = client.post("/api/model-metrics/evaluate?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert data["total_predictions"] == 50


def test_evaluate_model_performance_creates_record(client):
    """Test that evaluation creates a new model performance record."""
    # Generate demo data
    client.post("/api/demo/generate?count=100&anomaly_rate=0.2")
    
    # Get initial count
    initial_response = client.get("/api/model-metrics")
    initial_count = len(initial_response.json()["metrics"])
    
    # Evaluate
    client.post("/api/model-metrics/evaluate")
    
    # Check that a new record was created
    final_response = client.get("/api/model-metrics")
    final_count = len(final_response.json()["metrics"])
    assert final_count == initial_count + 1


def test_evaluate_model_performance_metrics_range(client):
    """Test that evaluation metrics are in valid ranges."""
    # Generate demo data
    client.post("/api/demo/generate?count=100&anomaly_rate=0.2")
    
    # Evaluate
    response = client.post("/api/model-metrics/evaluate")
    assert response.status_code == 200
    data = response.json()
    
    # Check that metrics are in valid ranges [0, 1]
    assert 0 <= data["precision"] <= 1
    assert 0 <= data["recall"] <= 1
    assert 0 <= data["f1_score"] <= 1
    assert 0 <= data["accuracy"] <= 1
    assert 0 <= data["avg_anomaly_score"] <= 1


def test_evaluate_model_performance_confusion_matrix(client):
    """Test that evaluation includes confusion matrix values."""
    # Generate demo data
    client.post("/api/demo/generate?count=100&anomaly_rate=0.2")
    
    # Evaluate
    response = client.post("/api/model-metrics/evaluate")
    assert response.status_code == 200
    data = response.json()
    
    # Check confusion matrix values
    assert "true_positives" in data
    assert "false_positives" in data
    assert "true_negatives" in data
    assert "false_negatives" in data
    
    # Sum should equal total predictions
    total = (data["true_positives"] + data["false_positives"] + 
             data["true_negatives"] + data["false_negatives"])
    assert total == data["total_predictions"]


def test_get_model_metrics_ordering(client, db_session):
    """Test that model metrics are returned in descending order by date."""
    from app.database.models import ModelPerformance
    
    # Create model performance records with different dates
    base_date = datetime.now(timezone.utc)
    for i in range(3):
        perf = ModelPerformance(
            model_version="v1",
            evaluation_date=base_date.replace(day=base_date.day - i),
            total_predictions=100,
            true_positives=10,
            false_positives=5,
            true_negatives=80,
            false_negatives=5,
            precision=0.67,
            recall=0.67,
            f1_score=0.67,
            accuracy=0.90,
            avg_anomaly_score=0.75,
            threshold_used=0.6
        )
        db_session.add(perf)
    db_session.commit()
    
    # Get metrics
    response = client.get("/api/model-metrics?limit=10")
    assert response.status_code == 200
    data = response.json()
    
    # Check that dates are in descending order
    dates = [m["evaluation_date"] for m in data["metrics"]]
    assert dates == sorted(dates, reverse=True)

