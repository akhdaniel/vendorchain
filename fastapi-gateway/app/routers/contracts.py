"""
Contract management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from ..database import get_db
from ..models import Contract, Vendor, WorkflowLog, ContractStatus
from ..schemas import (
    ContractCreate, ContractUpdate, ContractResponse,
    PaymentRecord, WorkflowLogResponse
)
from ..fabric_client import get_fabric_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/contracts",
    tags=["contracts"]
)


@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db)
) -> ContractResponse:
    """
    Create a new contract
    """
    try:
        # Verify vendor exists
        vendor = db.query(Vendor).filter(
            Vendor.vendor_id == contract.vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor {contract.vendor_id} not found"
            )
        
        # Check if contract ID already exists
        existing_contract = db.query(Contract).filter(
            Contract.contract_id == contract.contract_id
        ).first()
        
        if existing_contract:
            raise HTTPException(
                status_code=400,
                detail=f"Contract {contract.contract_id} already exists"
            )
        
        # Create contract in database
        db_contract = Contract(
            contract_id=contract.contract_id,
            vendor_id=vendor.id,  # Use internal vendor ID
            contract_type=contract.contract_type,
            description=contract.description,
            total_value=contract.total_value,
            # remaining_amount is a generated column, don't set it
            expiry_date=contract.expiry_date,
            created_by=contract.created_by,
            document_hash=contract.document_hash,
            status=ContractStatus.CREATED,
            payment_history=[]
        )
        
        # Create initial workflow log
        workflow_log = WorkflowLog(
            contract=db_contract,
            action="CREATE",
            to_status=ContractStatus.CREATED,
            performed_by=contract.created_by,
            notes=f"Contract created for vendor {vendor.name}"
        )
        
        db.add(db_contract)
        db.add(workflow_log)
        
        # Sync with blockchain
        try:
            fabric_client = await get_fabric_client()
            tx_id = await fabric_client.create_contract(
                contract_id=contract.contract_id,
                vendor_id=contract.vendor_id,
                contract_data={
                    "type": contract.contract_type.value,
                    "value": contract.total_value,
                    "expiry": contract.expiry_date.isoformat()
                },
                created_by=contract.created_by
            )
            
            if tx_id:
                db_contract.blockchain_tx_id = tx_id
                workflow_log.blockchain_tx_id = tx_id
        except Exception as e:
            logger.warning(f"Failed to sync contract to blockchain: {str(e)}")
        
        db.commit()
        db.refresh(db_contract)
        
        # Prepare response with vendor name
        response = ContractResponse(
            id=db_contract.id,
            contract_id=db_contract.contract_id,
            vendor_id=db_contract.vendor_id,
            vendor_name=vendor.name,
            contract_type=db_contract.contract_type,
            status=db_contract.status,
            description=db_contract.description,
            total_value=db_contract.total_value,
            paid_amount=db_contract.paid_amount or 0,
            remaining_amount=db_contract.remaining_amount or db_contract.total_value,
            payment_history=db_contract.payment_history or [],
            expiry_date=db_contract.expiry_date,
            document_hash=db_contract.document_hash,
            blockchain_tx_id=db_contract.blockchain_tx_id,
            created_by=db_contract.created_by,
            verified_by=db_contract.verified_by,
            verified_at=db_contract.verified_at,
            submitted_by=db_contract.submitted_by,
            submitted_at=db_contract.submitted_at,
            created_at=db_contract.created_at,
            updated_at=db_contract.updated_at
        )
        
        logger.info(f"Created contract: {contract.contract_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create contract: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create contract")


@router.get("/", response_model=List[ContractResponse])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ContractStatus] = None,
    vendor_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[ContractResponse]:
    """
    List all contracts with optional filtering
    """
    try:
        query = db.query(Contract).join(Vendor)
        
        if status:
            query = query.filter(Contract.status == status)
        
        if vendor_id:
            query = query.filter(Vendor.vendor_id == vendor_id)
        
        contracts = query.offset(skip).limit(limit).all()
        
        # Prepare responses with vendor names
        responses = []
        for contract in contracts:
            responses.append(ContractResponse(
                id=contract.id,
                contract_id=contract.contract_id,
                vendor_id=contract.vendor_id,
                vendor_name=contract.vendor.name,
                contract_type=contract.contract_type,
                status=contract.status,
                description=contract.description,
                total_value=contract.total_value,
                paid_amount=contract.paid_amount or 0,
                remaining_amount=contract.remaining_amount or contract.total_value,
                payment_history=contract.payment_history or [],
                expiry_date=contract.expiry_date,
                document_hash=contract.document_hash,
                blockchain_tx_id=contract.blockchain_tx_id,
                created_by=contract.created_by,
                verified_by=contract.verified_by,
                verified_at=contract.verified_at,
                submitted_by=contract.submitted_by,
                submitted_at=contract.submitted_at,
                created_at=contract.created_at,
                updated_at=contract.updated_at
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Failed to list contracts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contracts")


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    db: Session = Depends(get_db)
) -> ContractResponse:
    """
    Get contract by ID
    """
    try:
        contract = db.query(Contract).join(Vendor).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        response = ContractResponse(
            id=contract.id,
            contract_id=contract.contract_id,
            vendor_id=contract.vendor_id,
            vendor_name=contract.vendor.name,
            contract_type=contract.contract_type,
            status=contract.status,
            description=contract.description,
            total_value=contract.total_value,
            paid_amount=contract.paid_amount or 0,
            remaining_amount=contract.remaining_amount or contract.total_value,
            payment_history=contract.payment_history or [],
            expiry_date=contract.expiry_date,
            document_hash=contract.document_hash,
            blockchain_tx_id=contract.blockchain_tx_id,
            created_by=contract.created_by,
            verified_by=contract.verified_by,
            verified_at=contract.verified_at,
            submitted_by=contract.submitted_by,
            submitted_at=contract.submitted_at,
            created_at=contract.created_at,
            updated_at=contract.updated_at
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contract")


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db)
) -> ContractResponse:
    """
    Update contract information (limited fields)
    """
    try:
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Only allow updates to certain fields
        update_data = contract_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['description', 'total_value', 'expiry_date']:
                setattr(contract, field, value)
                
                # remaining_amount is a generated column, it will update automatically when total_value changes
        
        contract.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contract)
        
        # Prepare response
        response = ContractResponse(
            id=contract.id,
            contract_id=contract.contract_id,
            vendor_id=contract.vendor_id,
            vendor_name=contract.vendor.name,
            contract_type=contract.contract_type,
            status=contract.status,
            description=contract.description,
            total_value=contract.total_value,
            paid_amount=contract.paid_amount or 0,
            remaining_amount=contract.remaining_amount or contract.total_value,
            payment_history=contract.payment_history or [],
            expiry_date=contract.expiry_date,
            document_hash=contract.document_hash,
            blockchain_tx_id=contract.blockchain_tx_id,
            created_by=contract.created_by,
            verified_by=contract.verified_by,
            verified_at=contract.verified_at,
            submitted_by=contract.submitted_by,
            submitted_at=contract.submitted_at,
            created_at=contract.created_at,
            updated_at=contract.updated_at
        )
        
        logger.info(f"Updated contract: {contract_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update contract")


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a contract (only if in CREATED status)
    """
    try:
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Only allow deletion if in CREATED status
        if contract.status != ContractStatus.CREATED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete contract in {contract.status} status"
            )
        
        db.delete(contract)
        db.commit()
        
        logger.info(f"Deleted contract: {contract_id}")
        return {
            "message": f"Contract {contract_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete contract")


@router.post("/{contract_id}/payments", response_model=dict)
async def record_payment(
    contract_id: str,
    payment: PaymentRecord,
    db: Session = Depends(get_db)
) -> dict:
    """
    Record a payment for a contract
    """
    try:
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Update payment amounts
        contract.paid_amount = (contract.paid_amount or 0) + payment.amount
        # remaining_amount is a generated column, it will update automatically
        
        # Add to payment history
        if not contract.payment_history:
            contract.payment_history = []
        
        payment_entry = {
            "amount": payment.amount,
            "payment_date": payment.payment_date.isoformat(),
            "reference": payment.reference,
            "method": payment.method,
            "recorded_at": datetime.utcnow().isoformat()
        }
        contract.payment_history.append(payment_entry)
        
        # Sync with blockchain
        try:
            fabric_client = await get_fabric_client()
            tx_id = await fabric_client.record_payment(
                contract_id=contract_id,
                payment_data=payment_entry
            )
            
            if tx_id:
                payment_entry["blockchain_tx_id"] = tx_id
        except Exception as e:
            logger.warning(f"Failed to sync payment to blockchain: {str(e)}")
        
        contract.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Recorded payment for contract: {contract_id}")
        return {
            "message": "Payment recorded successfully",
            "paid_amount": contract.paid_amount,
            "remaining_amount": contract.remaining_amount,
            "blockchain_tx_id": payment_entry.get("blockchain_tx_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record payment for contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record payment")


@router.get("/{contract_id}/workflow-logs", response_model=List[WorkflowLogResponse])
async def get_workflow_logs(
    contract_id: str,
    db: Session = Depends(get_db)
) -> List[WorkflowLogResponse]:
    """
    Get workflow logs for a contract
    """
    try:
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        logs = db.query(WorkflowLog).filter(
            WorkflowLog.contract_id == contract.id
        ).order_by(WorkflowLog.performed_at.desc()).all()
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow logs for contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflow logs")