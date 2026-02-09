from sqlalchemy.orm import Session
from app import models, schemas

def get_inbound_shipment(db: Session, inbound_shipment_id: int):
    return db.query(models.InboundShipment).filter(models.InboundShipment.id == inbound_shipment_id).first()

def get_inbound_shipments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InboundShipment).offset(skip).limit(limit).all()

def create_inbound_shipment(db: Session, inbound_shipment: schemas.InboundShipmentCreate):
    db_inbound_shipment = models.InboundShipment(**inbound_shipment.model_dump())
    db.add(db_inbound_shipment)
    db.commit()
    db.refresh(db_inbound_shipment)
    return db_inbound_shipment

def update_inbound_shipment(db: Session, inbound_shipment_id: int, inbound_shipment: schemas.InboundShipmentUpdate):
    db_inbound_shipment = get_inbound_shipment(db, inbound_shipment_id)
    if db_inbound_shipment:
        update_data = inbound_shipment.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inbound_shipment, key, value)
        db.commit()
        db.refresh(db_inbound_shipment)
    return db_inbound_shipment

def delete_inbound_shipment(db: Session, inbound_shipment_id: int):
    db_inbound_shipment = get_inbound_shipment(db, inbound_shipment_id)
    if db_inbound_shipment:
        db.delete(db_inbound_shipment)
        db.commit()
    return db_inbound_shipment
