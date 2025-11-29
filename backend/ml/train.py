"""Train anomaly detection model."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
import pickle
import os
from pathlib import Path

# Create models directory if it doesn't exist
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "anomaly_detector_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"


def generate_training_data(n_samples=20000):
    """
    Generate synthetic training data with CLEAR separation for demo purposes.
    
    Normal traffic: Fast, successful, small-medium requests
    Anomalies: Very distinct patterns (server errors, very slow, very large)
    
    In production, you would use real historical data.
    """
    np.random.seed(42)
    
    data = []
    
    # Generate NORMAL traffic patterns - very distinct, healthy patterns
    for _ in range(int(n_samples * 0.95)):  # 95% normal
        data.append({
            "response_time_ms": max(10, np.random.normal(45, 12)),  # Fast: 10-100ms typical
            "status_code": np.random.choice([200, 201, 204], p=[0.85, 0.12, 0.03]),  # Always success
            "request_size_bytes": max(50, np.random.normal(800, 250)),  # Small-medium: 50-2000 bytes
            "response_size_bytes": max(100, np.random.normal(2500, 800)),  # Small-medium: 100-5000 bytes
            "hour_of_day": np.random.randint(0, 24),
            "day_of_week": np.random.randint(0, 7),
            "minute_of_hour": np.random.randint(0, 60),
            "is_error": 0,  # No errors
            "is_server_error": 0,  # No server errors
            "is_client_error": 0,  # No client errors
            "endpoint_length": max(5, np.random.normal(22, 6)),  # Normal endpoint lengths
            "method_get": np.random.choice([0, 1], p=[0.25, 0.75]),  # Mostly GET
            "method_post": np.random.choice([0, 1], p=[0.75, 0.25]),  # Some POST
        })
    
    # Generate ANOMALOUS traffic patterns - very distinct, clearly problematic
    for _ in range(int(n_samples * 0.05)):  # 5% anomalies
        anomaly_type = np.random.choice(["server_error", "very_slow", "very_large"], p=[0.4, 0.35, 0.25])
        
        if anomaly_type == "server_error":
            # Server errors: 5xx status codes, small responses
            data.append({
                "response_time_ms": np.random.normal(150, 50),  # Can be fast or slow
                "status_code": np.random.choice([500, 502, 503, 504], p=[0.5, 0.2, 0.2, 0.1]),  # Always 5xx
                "request_size_bytes": np.random.normal(800, 250),  # Normal request size
                "response_size_bytes": max(50, np.random.normal(150, 50)),  # Small error response
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 1,  # Error flag
                "is_server_error": 1,  # Server error flag
                "is_client_error": 0,
                "endpoint_length": np.random.normal(22, 6),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
        elif anomaly_type == "very_slow":
            # Very slow responses: >3000ms, but successful
            data.append({
                "response_time_ms": np.random.normal(5000, 1500),  # Very slow: 3000-10000ms
                "status_code": 200,  # But successful
                "request_size_bytes": np.random.normal(800, 250),  # Normal request
                "response_size_bytes": np.random.normal(2500, 800),  # Normal response
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 0,
                "is_server_error": 0,
                "is_client_error": 0,
                "endpoint_length": np.random.normal(22, 6),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
        else:  # very_large
            # Very large requests/responses: >10MB
            data.append({
                "response_time_ms": np.random.normal(200, 80),  # Normal response time
                "status_code": 200,  # Successful
                "request_size_bytes": np.random.normal(12000000, 3000000),  # Very large: 8-20MB
                "response_size_bytes": np.random.normal(20000000, 5000000),  # Very large: 10-30MB
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 0,
                "is_server_error": 0,
                "is_client_error": 0,
                "endpoint_length": np.random.normal(22, 6),
                "method_get": np.random.choice([0, 1], p=[0.2, 0.8]),  # Mostly GET for large
                "method_post": np.random.choice([0, 1], p=[0.8, 0.2]),
            })
    
    return pd.DataFrame(data)


def train_model():
    """Train the anomaly detection model."""
    print("Generating training data...")
    df = generate_training_data(n_samples=10000)
    
    # Add derived features (advanced feature engineering)
    df["response_to_request_ratio"] = df["response_size_bytes"] / df["request_size_bytes"].clip(lower=1)
    df["throughput_mbps"] = (df["response_size_bytes"] * 8) / (df["response_time_ms"].clip(lower=1) * 1000)
    df["is_very_slow"] = (df["response_time_ms"] > 3000).astype(float)
    df["is_very_large_request"] = (df["request_size_bytes"] > 10000000).astype(float)
    df["is_very_large_response"] = (df["response_size_bytes"] > 10000000).astype(float)
    
    # Feature order (must match feature_extractor)
    feature_columns = [
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
    
    X = df[feature_columns].values
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest with optimized parameters
    print("Training Isolation Forest model...")
    print("Using advanced ML techniques:")
    print("  - Isolation Forest (unsupervised anomaly detection)")
    print("  - StandardScaler for feature normalization")
    print("  - Optimized contamination and tree parameters")
    
    model = IsolationForest(
        contamination=0.05,  # Expect 5% anomalies (matches training data)
        random_state=42,
        n_estimators=200,  # More trees for better stability and performance
        max_samples='auto',  # Use all samples for each tree
        max_features=1.0,  # Use all features
        n_jobs=-1,  # Use all CPU cores for parallel training
        warm_start=False
    )
    model.fit(X_scaled)
    
    # Save model and scaler
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving scaler to {SCALER_PATH}...")
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    # Evaluate model on training data
    predictions = model.predict(X_scaled)
    n_anomalies = (predictions == -1).sum()
    
    # Create ground truth labels for evaluation
    y_true = (
        (df["status_code"] >= 500) |  # Server errors
        (df["response_time_ms"] > 3000) |  # Very slow
        (df["request_size_bytes"] > 10000000)  # Very large
    ).astype(int)
    y_pred = (predictions == -1).astype(int)
    
    # Calculate metrics
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    
    print(f"\n{'='*60}")
    print(f"Model Training Complete - Performance Metrics")
    print(f"{'='*60}")
    print(f"Total samples: {len(X):,}")
    print(f"Actual anomalies: {y_true.sum():,} ({y_true.sum()/len(X)*100:.1f}%)")
    print(f"Predicted anomalies: {n_anomalies:,} ({n_anomalies/len(X)*100:.1f}%)")
    print(f"\nTraining Performance:")
    print(f"  Precision: {precision:.2%}")
    print(f"  Recall: {recall:.2%}")
    print(f"  F1 Score: {f1:.2%}")
    print(f"  Accuracy: {accuracy:.2%}")
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_true, y_pred)
    print(f"  True Negatives:  {cm[0,0]:,}")
    print(f"  False Positives: {cm[0,1]:,}")
    print(f"  False Negatives: {cm[1,0]:,}")
    print(f"  True Positives:  {cm[1,1]:,}")
    print(f"\nModel saved to: {MODEL_PATH.absolute()}")
    print(f"Scaler saved to: {SCALER_PATH.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    train_model()

