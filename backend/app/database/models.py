"""Database models for SecuraFlow."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database.base import Base


class TrafficLog(Base):
    """Raw traffic log entries."""
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Metric(Base):
    """Aggregated metrics over time windows."""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    time_window = Column(DateTime(timezone=True), nullable=False, index=True)
    endpoint = Column(String(255), index=True)
    request_count = Column(Integer, nullable=False)
    avg_response_time_ms = Column(Float, nullable=False)
    error_count = Column(Integer, nullable=False, default=0)
    p95_response_time_ms = Column(Float)
    p99_response_time_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Anomaly(Base):
    """Detected anomalies."""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    traffic_log_id = Column(Integer, ForeignKey("traffic_logs.id"), nullable=True)
    anomaly_score = Column(Float, nullable=False)
    anomaly_type = Column(String(50), nullable=False)
    features = Column(JSON)
    is_resolved = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemHealth(Base):
    """System health metrics."""
    __tablename__ = "system_health"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    active_connections = Column(Integer)
    requests_per_second = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

