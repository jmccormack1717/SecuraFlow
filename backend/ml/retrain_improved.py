"""Retrain model with improved parameters for better performance."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import pickle
from pathlib import Path

# Create models directory if it doesn't exist
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "anomaly_detector_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"


def generate_training_data(n_samples=20000):
    """
    Generate synthetic training data with better separation.
    
    In production, you would use real historical data.
    """
    np.random.seed(42)
    
    data = []
    
    # Generate normal traffic patterns (more realistic)
    for _ in range(int(n_samples * 0.95)):  # 95% normal
        data.append({
            "response_time_ms": max(10, np.random.normal(50, 15)),  # 10-200ms typical
            "status_code": np.random.choice([200, 201, 204], p=[0.85, 0.12, 0.03]),
            "request_size_bytes": max(100, np.random.normal(800, 300)),
            "response_size_bytes": max(200, np.random.normal(3000, 1500)),
            "hour_of_day": np.random.randint(0, 24),
            "day_of_week": np.random.randint(0, 7),
            "minute_of_hour": np.random.randint(0, 60),
            "is_error": 0,
            "is_server_error": 0,
            "is_client_error": 0,
            "endpoint_length": max(5, np.random.normal(25, 8)),
            "method_get": np.random.choice([0, 1], p=[0.25, 0.75]),
            "method_post": np.random.choice([0, 1], p=[0.75, 0.25]),
        })
    
    # Generate anomalous traffic patterns (more distinct)
    for _ in range(int(n_samples * 0.05)):  # 5% anomalies
        anomaly_type = np.random.choice(["slow", "error", "large", "spike"], p=[0.3, 0.4, 0.2, 0.1])
        
        if anomaly_type == "slow":
            data.append({
                "response_time_ms": np.random.normal(3000, 800),  # Very slow
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
                "response_time_ms": np.random.normal(100, 50),
                "status_code": np.random.choice([500, 502, 503, 504], p=[0.5, 0.2, 0.2, 0.1]),
                "request_size_bytes": np.random.normal(1000, 500),
                "response_size_bytes": np.random.normal(200, 100),  # Small error responses
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
                "response_time_ms": np.random.normal(200, 100),
                "status_code": 200,
                "request_size_bytes": np.random.normal(8000000, 2000000),  # Very large
                "response_size_bytes": np.random.normal(15000000, 3000000),
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
                "response_time_ms": np.random.normal(5000, 1500),  # Extreme spike
                "status_code": np.random.choice([200, 500], p=[0.6, 0.4]),
                "request_size_bytes": np.random.normal(3000, 1500),
                "response_size_bytes": np.random.normal(10000, 4000),
                "hour_of_day": np.random.randint(0, 24),
                "day_of_week": np.random.randint(0, 7),
                "minute_of_hour": np.random.randint(0, 60),
                "is_error": np.random.choice([0, 1], p=[0.6, 0.4]),
                "is_server_error": np.random.choice([0, 1], p=[0.6, 0.4]),
                "is_client_error": 0,
                "endpoint_length": np.random.normal(35, 12),
                "method_get": np.random.choice([0, 1], p=[0.3, 0.7]),
                "method_post": np.random.choice([0, 1], p=[0.7, 0.3]),
            })
    
    return pd.DataFrame(data)


def train_improved_model():
    """Train an improved anomaly detection model."""
    print("Generating improved training data...")
    df = generate_training_data(n_samples=20000)
    
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
    
    # Create labels for evaluation (anomalies = server errors, very slow, or very large)
    y_true = (
        (df["status_code"] >= 500) |
        (df["response_time_ms"] > 2000) |
        (df["request_size_bytes"] > 10000000)
    ).astype(int)
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest with improved parameters
    print("Training improved Isolation Forest model...")
    model = IsolationForest(
        contamination=0.05,  # Expect 5% anomalies (reduced for better precision)
        random_state=42,
        n_estimators=200,  # More trees for better performance
        max_samples='auto',
        max_features=1.0,
        n_jobs=-1  # Use all CPU cores
    )
    model.fit(X_scaled)
    
    # Evaluate on training data
    predictions = model.predict(X_scaled)
    y_pred = (predictions == -1).astype(int)  # -1 = anomaly, 1 = normal
    
    print("\n" + "="*50)
    print("Model Training Results:")
    print("="*50)
    print(f"Total samples: {len(X)}")
    print(f"Actual anomalies: {y_true.sum()} ({y_true.sum()/len(X)*100:.1f}%)")
    print(f"Predicted anomalies: {y_pred.sum()} ({y_pred.sum()/len(X)*100:.1f}%)")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=['Normal', 'Anomaly']))
    
    # Save model and scaler
    print(f"\nSaving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving scaler to {SCALER_PATH}...")
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\n✅ Improved model trained and saved!")
    print(f"Model saved to: {MODEL_PATH.absolute()}")
    print(f"Scaler saved to: {SCALER_PATH.absolute()}")
    print("\nNote: The anomaly threshold has been increased to 0.85 for better precision.")


if __name__ == "__main__":
    train_improved_model()

