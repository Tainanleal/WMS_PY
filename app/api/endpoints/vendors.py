from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Vendor)
def create_vendor(
    *, 
    db: Session = Depends(deps.get_db),
    vendor_in: schemas.VendorCreate
):
    return crud.create_vendor(db=db, vendor=vendor_in)

@router.get("/", response_model=List[schemas.Vendor])
def read_vendors(
    db: Session = Depends(deps.get_db), 
    skip: int = 0, 
    limit: int = 100
):
    return crud.get_vendors(db, skip=skip, limit=limit)

@router.get("/{vendor_id}", response_model=schemas.Vendor)
def read_vendor(
    *, 
    db: Session = Depends(deps.get_db),
    vendor_id: int
):
    db_vendor = crud.get_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor

@router.put("/{vendor_id}", response_model=schemas.Vendor)
def update_vendor(
    *, 
    db: Session = Depends(deps.get_db),
    vendor_id: int,
    vendor_in: schemas.VendorUpdate
):
    db_vendor = crud.get_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return crud.update_vendor(db=db, vendor_id=vendor_id, vendor=vendor_in)

@router.delete("/{vendor_id}", response_model=schemas.Vendor)
def delete_vendor(
    *, 
    db: Session = Depends(deps.get_db),
    vendor_id: int
):
    db_vendor = crud.get_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return crud.delete_vendor(db=db, vendor_id=vendor_id)
