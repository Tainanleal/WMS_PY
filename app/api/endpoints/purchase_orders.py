from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.PurchaseOrder)
def create_purchase_order(
    *, 
    db: Session = Depends(deps.get_db),
    purchase_order_in: schemas.PurchaseOrderCreate
):
    return crud.create_purchase_order(db=db, purchase_order=purchase_order_in)

@router.get("/", response_model=List[schemas.PurchaseOrder])
def read_purchase_orders(
    db: Session = Depends(deps.get_db), 
    skip: int = 0, 
    limit: int = 100
):
    return crud.get_purchase_orders(db, skip=skip, limit=limit)

@router.get("/{purchase_order_id}", response_model=schemas.PurchaseOrder)
def read_purchase_order(
    *, 
    db: Session = Depends(deps.get_db),
    purchase_order_id: int
):
    db_purchase_order = crud.get_purchase_order(db, purchase_order_id=purchase_order_id)
    if db_purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return db_purchase_order

@router.put("/{purchase_order_id}", response_model=schemas.PurchaseOrder)
def update_purchase_order(
    *, 
    db: Session = Depends(deps.get_db),
    purchase_order_id: int,
    purchase_order_in: schemas.PurchaseOrderUpdate
):
    db_purchase_order = crud.get_purchase_order(db, purchase_order_id=purchase_order_id)
    if db_purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.update_purchase_order(db=db, purchase_order_id=purchase_order_id, purchase_order=purchase_order_in)

@router.delete("/{purchase_order_id}", response_model=schemas.PurchaseOrder)
def delete_purchase_order(
    *, 
    db: Session = Depends(deps.get_db),
    purchase_order_id: int
):
    db_purchase_order = crud.get_purchase_order(db, purchase_order_id=purchase_order_id)
    if db_purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.delete_purchase_order(db=db, purchase_order_id=purchase_order_id)
