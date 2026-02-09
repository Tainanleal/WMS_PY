from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/purchase-orders/{purchase_order_id}/items/", response_model=schemas.PurchaseOrderItem)
def create_purchase_order_item_for_order(purchase_order_id: int, purchase_order_item: schemas.PurchaseOrderItemCreate, db: Session = Depends(get_db)):
    db_purchase_order = crud.get_purchase_order(db, purchase_order_id=purchase_order_id)
    if not db_purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return crud.create_purchase_order_item(db=db, purchase_order_item=purchase_order_item, purchase_order_id=purchase_order_id)

@router.get("/purchase-orders/{purchase_order_id}/items/", response_model=List[schemas.PurchaseOrderItem])
def read_purchase_order_items_for_order(purchase_order_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_purchase_order = crud.get_purchase_order(db, purchase_order_id=purchase_order_id)
    if not db_purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    items = crud.get_purchase_order_items_by_order(db, purchase_order_id=purchase_order_id, skip=skip, limit=limit)
    return items

@router.get("/purchase-order-items/{purchase_order_item_id}", response_model=schemas.PurchaseOrderItem)
def read_purchase_order_item(purchase_order_item_id: int, db: Session = Depends(get_db)):
    db_purchase_order_item = crud.get_purchase_order_item(db, purchase_order_item_id=purchase_order_item_id)
    if db_purchase_order_item is None:
        raise HTTPException(status_code=404, detail="Purchase order item not found")
    return db_purchase_order_item

@router.put("/purchase-order-items/{purchase_order_item_id}", response_model=schemas.PurchaseOrderItem)
def update_purchase_order_item(purchase_order_item_id: int, purchase_order_item: schemas.PurchaseOrderItemUpdate, db: Session = Depends(get_db)):
    db_purchase_order_item = crud.update_purchase_order_item(db, purchase_order_item_id, purchase_order_item)
    if db_purchase_order_item is None:
        raise HTTPException(status_code=404, detail="Purchase order item not found")
    return db_purchase_order_item

@router.delete("/purchase-order-items/{purchase_order_item_id}", response_model=schemas.PurchaseOrderItem)
def delete_purchase_order_item(purchase_order_item_id: int, db: Session = Depends(get_db)):
    db_purchase_order_item = crud.delete_purchase_order_item(db, purchase_order_item_id)
    if db_purchase_order_item is None:
        raise HTTPException(status_code=404, detail="Purchase order item not found")
    return db_purchase_order_item
