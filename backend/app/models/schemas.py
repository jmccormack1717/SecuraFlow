"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class TrafficData(BaseModel):
    """Schema for incoming traffic data."""
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="HTTP status code")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    request_size_bytes: Optional[int] = Field(None, description="Request size in bytes")
    response_size_bytes: Optional[int] = Field(None, description="Response size in bytes")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    timestamp: Optional[datetime] = Field(None, description="Request timestamp")


class TrafficResponse(BaseModel):
    """Response for traffic ingestion."""
    success: bool
    anomaly_detected: bool
    anomaly_score: float
    message: Optional[str] = None


class MetricResponse(BaseModel):
    """Schema for metrics response."""
    time_window: datetime
    endpoint: Optional[str]
    request_count: int
    avg_response_time_ms: float
    error_count: int
    p95_response_time_ms: Optional[float]
    p99_response_time_ms: Optional[float]


class MetricsListResponse(BaseModel):
    """Response for metrics list."""
    metrics: List[MetricResponse]
    total: int


class AnomalyResponse(BaseModel):
    """Schema for anomaly response."""
    id: int
    detected_at: datetime
    anomaly_score: float
    anomaly_type: str
    features: Optional[Dict[str, Any]]
    is_resolved: bool
    traffic_log: Optional[Dict[str, Any]] = None


class AnomaliesListResponse(BaseModel):
    """Response for anomalies list."""
    anomalies: List[AnomalyResponse]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    model_loaded: bool
    uptime_seconds: float


class StatsResponse(BaseModel):
    """System statistics response."""
    total_requests: int
    total_anomalies: int
    avg_response_time_ms: float
    error_rate: float
    requests_per_second: float


class ModelPerformanceResponse(BaseModel):
    """Model performance metrics response."""
    id: int
    model_version: str
    evaluation_date: datetime
    total_predictions: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    auc_roc: Optional[float] = None
    avg_anomaly_score: float
    threshold_used: float


class ModelPerformanceListResponse(BaseModel):
    """List of model performance metrics."""
    metrics: List[ModelPerformanceResponse]
    total: int


class UserCreate(BaseModel):
    """Schema for user creation."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=6, description="Password")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None

