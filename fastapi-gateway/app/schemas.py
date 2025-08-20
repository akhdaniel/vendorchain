"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# Enumerations
class VendorTypeEnum(str, Enum):
    SUPPLIER = "SUPPLIER"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"
    CONTRACTOR = "CONTRACTOR"
    CONSULTANT = "CONSULTANT"


class VendorStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    BLACKLISTED = "BLACKLISTED"


class ContractTypeEnum(str, Enum):
    PURCHASE = "PURCHASE"
    SERVICE = "SERVICE"
    LEASE = "LEASE"
    MAINTENANCE = "MAINTENANCE"
    CONSULTING = "CONSULTING"


class ContractStatusEnum(str, Enum):
    CREATED = "CREATED"
    VERIFIED = "VERIFIED"
    SUBMITTED = "SUBMITTED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


# Vendor Schemas
class VendorBase(BaseModel):
    vendor_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    registration_number: Optional[str] = Field(None, max_length=100)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    vendor_type: VendorTypeEnum
    status: VendorStatusEnum = VendorStatusEnum.ACTIVE


class VendorCreate(VendorBase):
    blockchain_identity: Optional[str] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    status: Optional[VendorStatusEnum] = None


class VendorResponse(VendorBase):
    id: int
    blockchain_identity: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Contract Schemas
class ContractBase(BaseModel):
    contract_id: str = Field(..., min_length=1, max_length=50)
    vendor_id: str = Field(..., description="Vendor ID reference")
    contract_type: ContractTypeEnum
    description: Optional[str] = None
    total_value: float = Field(..., gt=0)
    expiry_date: date
    
    @validator('expiry_date')
    def expiry_date_future(cls, v):
        if v <= date.today():
            raise ValueError('Expiry date must be in the future')
        return v


class ContractCreate(ContractBase):
    created_by: str = Field(..., min_length=1, max_length=100)
    document_hash: Optional[str] = None


class ContractUpdate(BaseModel):
    description: Optional[str] = None
    total_value: Optional[float] = Field(None, gt=0)
    expiry_date: Optional[date] = None


class ContractResponse(BaseModel):
    id: int
    contract_id: str
    vendor_id: int
    vendor_name: Optional[str] = None
    contract_type: ContractTypeEnum
    status: ContractStatusEnum
    description: Optional[str] = None
    total_value: float
    paid_amount: float
    remaining_amount: float
    payment_history: List[Dict[str, Any]] = []
    expiry_date: date
    document_hash: Optional[str] = None
    blockchain_tx_id: Optional[str] = None
    created_by: str
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    submitted_by: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowTransition(BaseModel):
    performed_by: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class VerifyContractRequest(WorkflowTransition):
    verified_by: str = Field(..., min_length=1, max_length=100)


class SubmitContractRequest(WorkflowTransition):
    submitted_by: str = Field(..., min_length=1, max_length=100)


class PaymentRecord(BaseModel):
    amount: float = Field(..., gt=0)
    payment_date: date
    reference: str = Field(..., min_length=1, max_length=100)
    method: Optional[str] = Field(None, max_length=50)


class WorkflowLogResponse(BaseModel):
    id: int
    contract_id: int
    action: str
    from_status: Optional[ContractStatusEnum] = None
    to_status: ContractStatusEnum
    performed_by: str
    performed_at: datetime
    notes: Optional[str] = None
    blockchain_tx_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# Health Check Schemas
class HealthStatus(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.now)
    database: Optional[str] = None
    blockchain: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ReadinessCheck(BaseModel):
    ready: bool
    checks: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.now)


# Blockchain Schemas
class BlockchainSyncRequest(BaseModel):
    contract_id: str
    force: bool = False


class BlockchainSyncResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class BlockchainStatus(BaseModel):
    connected: bool
    peer_endpoint: str
    channel_name: str
    chaincode_name: str
    error: Optional[str] = None


# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


# Webhook Schemas
class WebhookEvent(BaseModel):
    event: str
    contract_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)