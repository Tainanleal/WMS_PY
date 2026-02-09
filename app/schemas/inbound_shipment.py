from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.inbound_shipment import InboundShipmentStatus
from .inbound_shipment_item import InboundShipmentItem

# --- Base Schema ---
class InboundShipmentBase(BaseModel):
    purchase_order_id: int
    arrival_date: Optional[date] = None
    status: InboundShipmentStatus = InboundShipmentStatus.EXPECTED

# --- Schema for Creating an Inbound Shipment ---
class InboundShipmentCreate(InboundShipmentBase):
    pass

# --- Schema for Updating an Inbound Shipment ---
class InboundShipmentUpdate(BaseModel):
    arrival_date: Optional[date] = None
    status: Optional[InboundShipmentStatus] = None

# --- Schema for Reading/Returning an Inbound Shipment ---
class InboundShipment(InboundShipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List['InboundShipmentItem'] = []

    class Config:
        from_attributes = True
