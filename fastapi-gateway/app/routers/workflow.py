"""
Contract workflow transition API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ..database import get_db
from ..models import Contract, WorkflowLog, ContractStatus
from ..schemas import (
    VerifyContractRequest, SubmitContractRequest,
    ContractResponse, APIResponse
)
from ..fabric_client import get_fabric_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"]
)


@router.post("/contracts/{contract_id}/verify", response_model=ContractResponse)
async def verify_contract(
    contract_id: str,
    request: VerifyContractRequest,
    db: Session = Depends(get_db)
) -> ContractResponse:
    """
    Verify a contract (transition from CREATED to VERIFIED)
    """
    try:
        # Get contract
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Check current status
        if contract.status != ContractStatus.CREATED:
            raise HTTPException(
                status_code=400,
                detail=f"Contract must be in CREATED status to verify. Current status: {contract.status}"
            )
        
        # Update contract status
        contract.status = ContractStatus.VERIFIED
        contract.verified_by = request.verified_by
        contract.verified_at = datetime.utcnow()
        contract.updated_at = datetime.utcnow()
        
        # Create workflow log
        workflow_log = WorkflowLog(
            contract_id=contract.id,
            action="VERIFY",
            from_status=ContractStatus.CREATED,
            to_status=ContractStatus.VERIFIED,
            performed_by=request.performed_by,
            notes=request.notes
        )
        
        # Sync with blockchain
        try:
            fabric_client = await get_fabric_client()
            tx_id = await fabric_client.verify_contract(
                contract_id=contract_id,
                verified_by=request.verified_by,
                notes=request.notes
            )
            
            if tx_id:
                workflow_log.blockchain_tx_id = tx_id
        except Exception as e:
            logger.warning(f"Failed to sync verification to blockchain: {str(e)}")
        
        db.add(workflow_log)
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
        
        logger.info(f"Contract {contract_id} verified by {request.verified_by}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to verify contract")


@router.post("/contracts/{contract_id}/submit", response_model=ContractResponse)
async def submit_contract(
    contract_id: str,
    request: SubmitContractRequest,
    db: Session = Depends(get_db)
) -> ContractResponse:
    """
    Submit a contract (transition from VERIFIED to SUBMITTED)
    """
    try:
        # Get contract
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Check current status
        if contract.status != ContractStatus.VERIFIED:
            raise HTTPException(
                status_code=400,
                detail=f"Contract must be in VERIFIED status to submit. Current status: {contract.status}"
            )
        
        # Update contract status
        contract.status = ContractStatus.SUBMITTED
        contract.submitted_by = request.submitted_by
        contract.submitted_at = datetime.utcnow()
        contract.updated_at = datetime.utcnow()
        
        # Create workflow log
        workflow_log = WorkflowLog(
            contract_id=contract.id,
            action="SUBMIT",
            from_status=ContractStatus.VERIFIED,
            to_status=ContractStatus.SUBMITTED,
            performed_by=request.performed_by,
            notes=request.notes
        )
        
        # Sync with blockchain
        try:
            fabric_client = await get_fabric_client()
            tx_id = await fabric_client.submit_contract(
                contract_id=contract_id,
                submitted_by=request.submitted_by,
                notes=request.notes
            )
            
            if tx_id:
                workflow_log.blockchain_tx_id = tx_id
        except Exception as e:
            logger.warning(f"Failed to sync submission to blockchain: {str(e)}")
        
        db.add(workflow_log)
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
        
        logger.info(f"Contract {contract_id} submitted by {request.submitted_by}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit contract")


@router.post("/contracts/{contract_id}/expire", response_model=APIResponse)
async def expire_contract(
    contract_id: str,
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Mark a contract as expired (automatic transition based on expiry date)
    """
    try:
        # Get contract
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Check if already expired
        if contract.status == ContractStatus.EXPIRED:
            return APIResponse(
                success=True,
                message="Contract is already expired",
                data={"contract_id": contract_id, "status": "EXPIRED"}
            )
        
        # Check expiry date
        from datetime import date
        if contract.expiry_date > date.today():
            raise HTTPException(
                status_code=400,
                detail=f"Contract expiry date is {contract.expiry_date}. Cannot expire before this date."
            )
        
        # Update contract status
        old_status = contract.status
        contract.status = ContractStatus.EXPIRED
        contract.updated_at = datetime.utcnow()
        
        # Create workflow log
        workflow_log = WorkflowLog(
            contract_id=contract.id,
            action="EXPIRE",
            from_status=old_status,
            to_status=ContractStatus.EXPIRED,
            performed_by="SYSTEM",
            notes="Contract expired based on expiry date"
        )
        
        db.add(workflow_log)
        db.commit()
        
        logger.info(f"Contract {contract_id} marked as expired")
        return APIResponse(
            success=True,
            message="Contract marked as expired",
            data={
                "contract_id": contract_id,
                "status": "EXPIRED",
                "previous_status": old_status.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to expire contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to expire contract")


@router.post("/contracts/{contract_id}/terminate", response_model=APIResponse)
async def terminate_contract(
    contract_id: str,
    reason: str,
    terminated_by: str,
    db: Session = Depends(get_db)
) -> APIResponse:
    """
    Terminate a contract (can be done from any status)
    """
    try:
        # Get contract
        contract = db.query(Contract).filter(
            Contract.contract_id == contract_id
        ).first()
        
        if not contract:
            raise HTTPException(
                status_code=404,
                detail=f"Contract {contract_id} not found"
            )
        
        # Check if already terminated
        if contract.status == ContractStatus.TERMINATED:
            return APIResponse(
                success=True,
                message="Contract is already terminated",
                data={"contract_id": contract_id, "status": "TERMINATED"}
            )
        
        # Update contract status
        old_status = contract.status
        contract.status = ContractStatus.TERMINATED
        contract.updated_at = datetime.utcnow()
        
        # Create workflow log
        workflow_log = WorkflowLog(
            contract_id=contract.id,
            action="TERMINATE",
            from_status=old_status,
            to_status=ContractStatus.TERMINATED,
            performed_by=terminated_by,
            notes=f"Termination reason: {reason}"
        )
        
        db.add(workflow_log)
        db.commit()
        
        logger.info(f"Contract {contract_id} terminated by {terminated_by}")
        return APIResponse(
            success=True,
            message="Contract terminated successfully",
            data={
                "contract_id": contract_id,
                "status": "TERMINATED",
                "previous_status": old_status.value,
                "terminated_by": terminated_by
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to terminate contract {contract_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to terminate contract")