"""Train anomaly detection model."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os
from pathlib import Path

# Create models directory if it doesn't exist
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "anomaly_detector_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"


def generate_training_data(n_samples=10000):
    """
    Generate synthetic training data.
    
    In production, you would use real historical data.
    """
    np.random.seed(42)
    
    data = []
    
    # Generate normal traffic patterns
    for _ in range(int(n_samples * 0.9)):
        data.append({
            "response_time_ms": np.random.normal(50, 20),
            "status_code": np.random.choice([200, 201, 204], p=[0.8, 0.15, 0.05]),
            "request_size_bytes": np.random.normal(1000, 500),
            "response_size_bytes": np.random.normal(5000, 2000),
            "hour_of_day": np.random.randint(0, 24),
            "day_of_week": np.random.randint(0, 7),
            "minute_of_hour": np.random.randint(0, 60),
            "is_error": 0,
            "is_server_error": 0,
            "is_client_error": 0,
            "endpoint_length": np.random.normal(20, 10),
            "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
            "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
        })
    
    # Generate anomalous traffic patterns
    for _ in range(int(n_samples * 0.1)):
        anomaly_type = np.random.choice(["slow", "error", "large", "spike"])
        
        if anomaly_type == "slow":
            data.append({
                "response_time_ms": np.random.normal(2000, 500),
                "status_code": 200,
                "request_size_bytes": np.random.normal(1000, 500),
                "response_size_bytes": np.random.normal(5000, 2000),
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 0,
                "is_server_error": 0,
                "is_client_error": 0,
                "endpoint_length": np.random.normal(20, 10),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
        elif anomaly_type == "error":
            data.append({
                "response_time_ms": np.random.normal(50, 20),
                "status_code": np.random.choice([500, 502, 503], p=[0.5, 0.3, 0.2]),
                "request_size_bytes": np.random.normal(1000, 500),
                "response_size_bytes": np.random.normal(500, 200),
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 1,
                "is_server_error": 1,
                "is_client_error": 0,
                "endpoint_length": np.random.normal(20, 10),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
        elif anomaly_type == "large":
            data.append({
                "response_time_ms": np.random.normal(100, 30),
                "status_code": 200,
                "request_size_bytes": np.random.normal(5000000, 1000000),
                "response_size_bytes": np.random.normal(10000000, 2000000),
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": 0,
                "is_server_error": 0,
                "is_client_error": 0,
                "endpoint_length": np.random.normal(20, 10),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
        else:  # spike
            data.append({
                "response_time_ms": np.random.normal(3000, 1000),
                "status_code": np.random.choice([200, 500], p=[0.7, 0.3]),
                "request_size_bytes": np.random.normal(2000, 1000),
                "response_size_bytes": np.random.normal(8000, 3000),
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": np.random.choice([0, 1], p=[0.7, 0.3]),
                "is_server_error": np.random.choice([0, 1], p=[0.7, 0.3]),
                "is_client_error": 0,
                "endpoint_length": np.random.normal(30, 15),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
    
    return pd.DataFrame(data)


def train_model():
    """Train the anomaly detection model."""
    print("Generating training data...")
    df = generate_training_data(n_samples=10000)
    
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
    ]
    
    X = df[feature_columns].values
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    print("Training Isolation Forest model...")
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100
    )
    model.fit(X_scaled)
    
    # Save model and scaler
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving scaler to {SCALER_PATH}...")
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    # Evaluate model
    predictions = model.predict(X_scaled)
    n_anomalies = (predictions == -1).sum()
    print(f"\nModel trained successfully!")
    print(f"Total samples: {len(X)}")
    print(f"Detected anomalies: {n_anomalies} ({n_anomalies/len(X)*100:.1f}%)")
    print(f"Model saved to: {MODEL_PATH.absolute()}")


if __name__ == "__main__":
    train_model()

