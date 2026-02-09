from sqlalchemy.orm import Session
from app import models, schemas

def get_purchase_order_item(db: Session, purchase_order_item_id: int):
    return db.query(models.PurchaseOrderItem).filter(models.PurchaseOrderItem.id == purchase_order_item_id).first()

def get_purchase_order_items_by_order(db: Session, purchase_order_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.PurchaseOrderItem).filter(models.PurchaseOrderItem.purchase_order_id == purchase_order_id).offset(skip).limit(limit).all()

def create_purchase_order_item(db: Session, purchase_order_item: schemas.PurchaseOrderItemCreate, purchase_order_id: int):
    db_purchase_order_item = models.PurchaseOrderItem(**purchase_order_item.model_dump(), purchase_order_id=purchase_order_id)
    db.add(db_purchase_order_item)
    db.commit()
    db.refresh(db_purchase_order_item)
    return db_purchase_order_item

def update_purchase_order_item(db: Session, purchase_order_item_id: int, purchase_order_item: schemas.PurchaseOrderItemUpdate):
    db_purchase_order_item = get_purchase_order_item(db, purchase_order_item_id)
    if db_purchase_order_item:
        update_data = purchase_order_item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_purchase_order_item, key, value)
        db.commit()
        db.refresh(db_purchase_order_item)
    return db_purchase_order_item

def delete_purchase_order_item(db: Session, purchase_order_item_id: int):
    db_purchase_order_item = get_purchase_order_item(db, purchase_order_item_id)
    if db_purchase_order_item:
        db.delete(db_purchase_order_item)
        db.commit()
    return db_purchase_order_item
