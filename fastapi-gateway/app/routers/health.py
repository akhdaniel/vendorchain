"""
Health check and readiness API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from datetime import datetime
import logging

from ..database import get_db, check_database_connection
from ..fabric_client import get_fabric_client
from ..schemas import HealthStatus, ReadinessCheck
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"]
)


@router.get("/", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Basic health check endpoint
    """
    return HealthStatus(
        status="healthy",
        service="vendorchain-api-gateway",
        timestamp=datetime.utcnow()
    )


@router.get("/live", response_model=HealthStatus)
async def liveness_probe() -> HealthStatus:
    """
    Kubernetes liveness probe endpoint
    """
    return HealthStatus(
        status="alive",
        service="vendorchain-api-gateway",
        timestamp=datetime.utcnow()
    )


@router.get("/ready", response_model=ReadinessCheck)
async def readiness_probe(db: Session = Depends(get_db)) -> ReadinessCheck:
    """
    Kubernetes readiness probe endpoint
    Checks database and blockchain connectivity
    """
    checks = {
        "database": False,
        "blockchain": False
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database readiness check failed: {str(e)}")
    
    # Check blockchain
    try:
        fabric_client = await get_fabric_client()
        if await fabric_client.check_connection():
            checks["blockchain"] = True
    except Exception as e:
        logger.error(f"Blockchain readiness check failed: {str(e)}")
    
    # Service is ready if all checks pass
    ready = all(checks.values())
    
    return ReadinessCheck(
        ready=ready,
        checks=checks,
        timestamp=datetime.utcnow()
    )


@router.get("/database", response_model=HealthStatus)
async def database_health(db: Session = Depends(get_db)) -> HealthStatus:
    """
    Database connectivity health check
    """
    try:
        # Execute a simple query
        result = db.execute(text("SELECT version()")).fetchone()
        
        return HealthStatus(
            status="healthy",
            service="database",
            database="connected",
            timestamp=datetime.utcnow(),
            details={
                "version": result[0] if result else None,
                "pool_size": settings.db_pool_size
            }
        )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return HealthStatus(
            status="unhealthy",
            service="database",
            database="disconnected",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        )


@router.get("/blockchain", response_model=HealthStatus)
async def blockchain_health() -> HealthStatus:
    """
    Blockchain connectivity health check
    """
    try:
        fabric_client = await get_fabric_client()
        connected = await fabric_client.check_connection()
        
        if connected:
            return HealthStatus(
                status="healthy",
                service="blockchain",
                blockchain="connected",
                timestamp=datetime.utcnow(),
                details={
                    "peer": settings.fabric_peer_endpoint,
                    "channel": settings.fabric_channel_name,
                    "chaincode": settings.fabric_chaincode_name
                }
            )
        else:
            return HealthStatus(
                status="unhealthy",
                service="blockchain",
                blockchain="disconnected",
                timestamp=datetime.utcnow(),
                details={"error": "Connection check failed"}
            )
    except Exception as e:
        logger.error(f"Blockchain health check failed: {str(e)}")
        return HealthStatus(
            status="unhealthy",
            service="blockchain",
            blockchain="error",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        )