from sqlalchemy.orm import Session
from app.models.inbound_shipment_item import InboundShipmentItem
from app.schemas.inbound_shipment_item import InboundShipmentItemCreate, InboundShipmentItemUpdate

def get_inbound_shipment_item(db: Session, item_id: int):
    return db.query(InboundShipmentItem).filter(InboundShipmentItem.id == item_id).first()

def get_inbound_shipment_items_by_shipment(
    db: Session, shipment_id: int, skip: int = 0, limit: int = 100
):
    return (
        db.query(InboundShipmentItem)
        .filter(InboundShipmentItem.inbound_shipment_id == shipment_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_inbound_shipment_item(db: Session, item: InboundShipmentItemCreate):
    db_item = InboundShipmentItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_inbound_shipment_item(
    db: Session, item_id: int, item: InboundShipmentItemUpdate
):
    db_item = get_inbound_shipment_item(db, item_id)
    if db_item:
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_inbound_shipment_item(db: Session, item_id: int):
    db_item = get_inbound_shipment_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
