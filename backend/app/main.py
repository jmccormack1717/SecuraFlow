"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import traffic, metrics, anomalies, health, demo
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Real-time API monitoring and anomaly detection system"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(traffic.router)
app.include_router(metrics.router)
app.include_router(anomalies.router)
app.include_router(health.router)
app.include_router(demo.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SecuraFlow API",
        "version": settings.api_version,
        "status": "running"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("SecuraFlow API starting up...")
    logger.info(f"API Version: {settings.api_version}")
    
    # Initialize database tables if they don't exist
    try:
        from app.database.base import Base, engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        # Don't fail startup if tables already exist


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("SecuraFlow API shutting down...")

