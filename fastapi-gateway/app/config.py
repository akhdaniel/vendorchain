"""
Configuration settings for VendorChain FastAPI Gateway
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "VendorChain API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://odoo:odoo@postgres:5432/vendorchain"
    )
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_pool_timeout: int = 30
    
    # Fabric Network
    fabric_peer_endpoint: str = os.getenv(
        "FABRIC_PEER_ENDPOINT",
        "peer0.org1.vendorchain.com:7051"
    )
    fabric_orderer_endpoint: str = os.getenv(
        "FABRIC_ORDERER_ENDPOINT", 
        "orderer.vendorchain.com:7050"
    )
    fabric_ca_endpoint: str = os.getenv(
        "FABRIC_CA_ENDPOINT",
        "ca.org1.vendorchain.com:7054"
    )
    fabric_channel_name: str = os.getenv(
        "FABRIC_CHANNEL_NAME",
        "vendorcontract"
    )
    fabric_chaincode_name: str = os.getenv(
        "FABRIC_CHAINCODE_NAME",
        "vendor-contract"
    )
    fabric_msp_id: str = "Org1MSP"
    fabric_wallet_path: str = "/app/fabric-config/wallet"
    fabric_connection_profile: str = "/app/fabric-config/connection-profile.json"
    
    # Security
    api_key_enabled: bool = False
    api_key_header: str = "X-API-Key"
    cors_origins: list = ["http://localhost:8069", "http://odoo:8069"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()