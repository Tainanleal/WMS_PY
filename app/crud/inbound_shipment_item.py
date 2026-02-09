from sqlalchemy.orm import Session
from app import models, schemas

def get_inbound_shipment_item(db: Session, inbound_shipment_item_id: int):
    return db.query(models.InboundShipmentItem).filter(models.InboundShipmentItem.id == inbound_shipment_item_id).first()

def get_inbound_shipment_items_by_shipment(db: Session, inbound_shipment_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.InboundShipmentItem)
        .filter(models.InboundShipmentItem.inbound_shipment_id == inbound_shipment_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_inbound_shipment_item(db: Session, inbound_shipment_item: schemas.InboundShipmentItemCreate, inbound_shipment_id: int):
    db_inbound_shipment_item = models.InboundShipmentItem(**inbound_shipment_item.model_dump(), inbound_shipment_id=inbound_shipment_id)
    db.add(db_inbound_shipment_item)
    db.commit()
    db.refresh(db_inbound_shipment_item)
    return db_inbound_shipment_item

def update_inbound_shipment_item(db: Session, inbound_shipment_item_id: int, inbound_shipment_item: schemas.InboundShipmentItemUpdate):
    db_inbound_shipment_item = get_inbound_shipment_item(db, inbound_shipment_item_id)
    if db_inbound_shipment_item:
        update_data = inbound_shipment_item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inbound_shipment_item, key, value)
        db.commit()
        db.refresh(db_inbound_shipment_item)
    return db_inbound_shipment_item

def delete_inbound_shipment_item(db: Session, inbound_shipment_item_id: int):
    db_inbound_shipment_item = get_inbound_shipment_item(db, inbound_shipment_item_id)
    if db_inbound_shipment_item:
        db.delete(db_inbound_shipment_item)
        db.commit()
    return db_inbound_shipment_item
