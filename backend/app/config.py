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
    anomaly_threshold: float = 0.7
    
    # API
    api_title: str = "SecuraFlow API"
    api_version: str = "1.0.0"
    # Store as string to avoid JSON parsing issues with pydantic-settings
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173"
    
    # Logging
    log_level: str = "INFO"
    
    # Metrics aggregation
    metrics_window_seconds: int = 60  # Aggregate metrics every minute
    
    # Rate limiting
    rate_limit_per_minute: int = 60  # Requests per minute per IP
    rate_limit_enabled: bool = True
    
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

