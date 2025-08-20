"""
SQLAlchemy database models for VendorChain
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, JSON, Date, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class VendorType(str, enum.Enum):
    """Vendor type enumeration"""
    SUPPLIER = "SUPPLIER"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"
    CONTRACTOR = "CONTRACTOR"
    CONSULTANT = "CONSULTANT"


class VendorStatus(str, enum.Enum):
    """Vendor status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    BLACKLISTED = "BLACKLISTED"


class ContractType(str, enum.Enum):
    """Contract type enumeration"""
    PURCHASE = "PURCHASE"
    SERVICE = "SERVICE"
    LEASE = "LEASE"
    MAINTENANCE = "MAINTENANCE"
    CONSULTING = "CONSULTING"


class ContractStatus(str, enum.Enum):
    """Contract status enumeration"""
    CREATED = "CREATED"
    VERIFIED = "VERIFIED"
    SUBMITTED = "SUBMITTED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class Vendor(Base):
    """Vendor model"""
    __tablename__ = "vendor_contract_management_vendor"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(100))
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    address = Column(Text)
    vendor_type = Column(Enum(VendorType), nullable=False, default=VendorType.SUPPLIER)
    status = Column(Enum(VendorStatus), nullable=False, default=VendorStatus.ACTIVE)
    blockchain_identity = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contracts = relationship("Contract", back_populates="vendor")


class Contract(Base):
    """Contract model"""
    __tablename__ = "vendor_contract_management_contract"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_contract_management_vendor.id"), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.CREATED)
    description = Column(Text)
    total_value = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0)
    remaining_amount = Column(Float, Computed("total_value - paid_amount", persisted=True))
    payment_history = Column(JSON, default=list)
    expiry_date = Column(Date, nullable=False)
    document_hash = Column(String(255))
    blockchain_tx_id = Column(String(255), index=True)
    created_by = Column(String(100), nullable=False)
    verified_by = Column(String(100))
    verified_at = Column(DateTime(timezone=True))
    submitted_by = Column(String(100))
    submitted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    odoo_user_id = Column(Integer)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")
    workflow_logs = relationship("WorkflowLog", back_populates="contract", cascade="all, delete-orphan")
    api_metadata = relationship("APIMetadata", back_populates="contract")


class WorkflowLog(Base):
    """Workflow log model"""
    __tablename__ = "vendor_contract_management_workflow_log"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("vendor_contract_management_contract.id"), nullable=False)
    action = Column(String(50), nullable=False)
    from_status = Column(Enum(ContractStatus))
    to_status = Column(Enum(ContractStatus), nullable=False)
    performed_by = Column(String(100), nullable=False)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    blockchain_tx_id = Column(String(255))
    odoo_user_id = Column(Integer)
    
    # Relationships
    contract = relationship("Contract", back_populates="workflow_logs")


class APIMetadata(Base):
    """API metadata model"""
    __tablename__ = "vendor_contract_api_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("vendor_contract_management_contract.id"))
    api_endpoint = Column(String(255), nullable=False)
    http_method = Column(String(10), nullable=False)
    request_payload = Column(JSON)
    response_payload = Column(JSON)
    status_code = Column(Integer)
    blockchain_sync = Column(Integer, default=0)  # Boolean as integer
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="api_metadata")