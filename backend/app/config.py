"""Configuration management for SecuraFlow backend."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://user:password@localhost/securaflow"
    
    # ML Model
    model_path: str = "./models/anomaly_detector_v1.pkl"
    anomaly_threshold: float = 0.7
    
    # API
    api_title: str = "SecuraFlow API"
    api_version: str = "1.0.0"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"
    
    # Metrics aggregation
    metrics_window_seconds: int = 60  # Aggregate metrics every minute
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

