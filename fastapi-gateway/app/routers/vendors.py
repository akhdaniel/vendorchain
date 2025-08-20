"""
Vendor management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..models import Vendor, VendorStatus
from ..schemas import VendorCreate, VendorUpdate, VendorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vendors",
    tags=["vendors"]
)


@router.post("/", response_model=VendorResponse)
async def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db)
) -> VendorResponse:
    """
    Create a new vendor
    """
    try:
        # Check if vendor ID already exists
        existing_vendor = db.query(Vendor).filter(
            Vendor.vendor_id == vendor.vendor_id
        ).first()
        
        if existing_vendor:
            raise HTTPException(
                status_code=400,
                detail=f"Vendor with ID {vendor.vendor_id} already exists"
            )
        
        # Create new vendor
        db_vendor = Vendor(**vendor.dict())
        db.add(db_vendor)
        db.commit()
        db.refresh(db_vendor)
        
        logger.info(f"Created vendor: {vendor.vendor_id}")
        return db_vendor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create vendor: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create vendor")


@router.get("/", response_model=List[VendorResponse])
async def list_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[VendorStatus] = None,
    db: Session = Depends(get_db)
) -> List[VendorResponse]:
    """
    List all vendors with optional filtering
    """
    try:
        query = db.query(Vendor)
        
        if status:
            query = query.filter(Vendor.status == status)
        
        vendors = query.offset(skip).limit(limit).all()
        return vendors
        
    except Exception as e:
        logger.error(f"Failed to list vendors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vendors")


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    db: Session = Depends(get_db)
) -> VendorResponse:
    """
    Get vendor by ID
    """
    try:
        vendor = db.query(Vendor).filter(
            Vendor.vendor_id == vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor {vendor_id} not found"
            )
        
        return vendor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendor {vendor_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vendor")


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor_update: VendorUpdate,
    db: Session = Depends(get_db)
) -> VendorResponse:
    """
    Update vendor information
    """
    try:
        vendor = db.query(Vendor).filter(
            Vendor.vendor_id == vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor {vendor_id} not found"
            )
        
        # Update only provided fields
        update_data = vendor_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)
        
        db.commit()
        db.refresh(vendor)
        
        logger.info(f"Updated vendor: {vendor_id}")
        return vendor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update vendor {vendor_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update vendor")


@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a vendor (soft delete by setting status to INACTIVE)
    """
    try:
        vendor = db.query(Vendor).filter(
            Vendor.vendor_id == vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor {vendor_id} not found"
            )
        
        # Check if vendor has contracts
        if vendor.contracts:
            # Soft delete - set status to INACTIVE
            vendor.status = VendorStatus.INACTIVE
            db.commit()
            
            logger.info(f"Soft deleted vendor: {vendor_id}")
            return {
                "message": f"Vendor {vendor_id} deactivated (has existing contracts)",
                "status": "inactive"
            }
        else:
            # Hard delete if no contracts
            db.delete(vendor)
            db.commit()
            
            logger.info(f"Deleted vendor: {vendor_id}")
            return {
                "message": f"Vendor {vendor_id} deleted successfully",
                "status": "deleted"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete vendor {vendor_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete vendor")