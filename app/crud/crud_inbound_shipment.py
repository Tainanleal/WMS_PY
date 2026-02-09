from sqlalchemy.orm import Session
from app.models.inbound_shipment import InboundShipment, InboundShipmentStatus
from app.schemas.inbound_shipment import InboundShipmentCreate, InboundShipmentUpdate

def get_inbound_shipment(db: Session, shipment_id: int):
    return db.query(InboundShipment).filter(InboundShipment.id == shipment_id).first()

def get_inbound_shipments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(InboundShipment).offset(skip).limit(limit).all()

def create_inbound_shipment(db: Session, shipment: InboundShipmentCreate):
    db_shipment = InboundShipment(**shipment.dict())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

def update_inbound_shipment_status(db: Session, shipment_id: int, status: InboundShipmentStatus):
    db_shipment = get_inbound_shipment(db, shipment_id)
    if db_shipment:
        db_shipment.status = status
        db.commit()
        db.refresh(db_shipment)
    return db_shipment

def update_inbound_shipment(db: Session, shipment_id: int, shipment: InboundShipmentUpdate):
    db_shipment = get_inbound_shipment(db, shipment_id)
    if db_shipment:
        update_data = shipment.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_shipment, key, value)
        db.commit()
        db.refresh(db_shipment)
    return db_shipment

def delete_inbound_shipment(db: Session, shipment_id: int):
    db_shipment = get_inbound_shipment(db, shipment_id)
    if db_shipment:
        db.delete(db_shipment)
        db.commit()
    return db_shipment
