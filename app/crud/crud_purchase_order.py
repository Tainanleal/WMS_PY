from sqlalchemy.orm import Session
from app import models, schemas

def get_purchase_order(db: Session, purchase_order_id: int):
    return db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == purchase_order_id).first()

def get_purchase_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PurchaseOrder).offset(skip).limit(limit).all()

def create_purchase_order(db: Session, purchase_order: schemas.PurchaseOrderCreate):
    db_purchase_order = models.PurchaseOrder(**purchase_order.dict())
    db.add(db_purchase_order)
    db.commit()
    db.refresh(db_purchase_order)
    return db_purchase_order

def update_purchase_order(db: Session, purchase_order_id: int, purchase_order: schemas.PurchaseOrderUpdate):
    db_purchase_order = get_purchase_order(db, purchase_order_id)
    if db_purchase_order:
        update_data = purchase_order.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_purchase_order, key, value)
        db.commit()
        db.refresh(db_purchase_order)
    return db_purchase_order

def delete_purchase_order(db: Session, purchase_order_id: int):
    db_purchase_order = get_purchase_order(db, purchase_order_id)
    if db_purchase_order:
        db.delete(db_purchase_order)
        db.commit()
    return db_purchase_order
