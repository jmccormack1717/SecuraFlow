"""Configuration management for SecuraFlow backend."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


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
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

