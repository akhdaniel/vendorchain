"""
VendorChain MVP FastAPI Gateway
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any

from .config import settings
from .database import init_database
from .fabric_client import get_fabric_client, close_fabric_client

# Import routers
from .routers import vendors, contracts, workflow, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting VendorChain FastAPI Gateway...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    # Initialize Fabric SDK connection
    try:
        fabric_client = await get_fabric_client()
        logger.info("Fabric client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Fabric client: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down VendorChain FastAPI Gateway...")
    
    # Close Fabric SDK connection
    try:
        await close_fabric_client()
        logger.info("Fabric client closed successfully")
    except Exception as e:
        logger.error(f"Error closing Fabric client: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="API Gateway for VendorChain blockchain integration",
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(vendors.router)
app.include_router(contracts.router)
app.include_router(workflow.router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning basic API information"""
    return {
        "service": "VendorChain MVP API Gateway",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container health monitoring"""
    try:
        # TODO: Add database connectivity check
        # TODO: Add Fabric network connectivity check
        
        return {
            "status": "healthy",
            "service": "vendorchain-fastapi-gateway",
            "timestamp": "2025-08-19T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/health/database")
async def database_health() -> Dict[str, str]:
    """Database connectivity health check"""
    try:
        # TODO: Implement actual database connectivity check
        # For now, return a placeholder response
        return {
            "database": "connected",
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unhealthy")


@app.get("/health/fabric")
async def fabric_health() -> Dict[str, str]:
    """Fabric network connectivity health check"""
    try:
        # TODO: Implement actual Fabric connectivity check
        # For now, return a placeholder response
        return {
            "fabric": "connected",
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Fabric health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Fabric network unhealthy")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )