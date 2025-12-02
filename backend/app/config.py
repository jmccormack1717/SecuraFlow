"""Configuration management for SecuraFlow backend."""
from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://user:password@localhost/securaflow"
    
    # ML Model
    model_path: str = "./models/anomaly_detector_v1.pkl"
    anomaly_threshold: float = 0.6  # Lowered for better detection of clear anomalies
    
    # API
    api_title: str = "SecuraFlow API"
    api_version: str = "1.0.0"
    # Store as string to avoid JSON parsing issues with pydantic-settings
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173,https://securaflow-frontend.onrender.com"
    
    # Logging
    log_level: str = "INFO"
    structured_logging: bool = True  # Enable JSON structured logging
    
    # Metrics aggregation
    metrics_window_seconds: int = 60  # Aggregate metrics every minute
    
    # Model evaluation
    model_evaluation_logs: int = 500  # Evaluate model performance over last N traffic logs
    
    # Rate limiting
    rate_limit_per_minute: int = 60  # Requests per minute per IP
    rate_limit_enabled: bool = True
    
    # Authentication
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")  # MUST be set in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins string into list."""
        # Get from environment variable if set, otherwise use default
        cors_str = os.getenv('CORS_ORIGINS', self.cors_origins_str)
        return [
            origin.strip() 
            for origin in cors_str.split(',') 
            if origin.strip()
        ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

