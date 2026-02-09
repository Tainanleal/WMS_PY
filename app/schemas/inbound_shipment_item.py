from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Base Schema ---
class InboundShipmentItemBase(BaseModel):
    product_id: int
    quantity_received: int

# --- Schema for Creating an Inbound Shipment Item ---
class InboundShipmentItemCreate(InboundShipmentItemBase):
    pass

# --- Schema for Updating an Inbound Shipment Item ---
class InboundShipmentItemUpdate(BaseModel):
    quantity_received: Optional[int] = None

# --- Schema for Reading/Returning an Inbound Shipment Item ---
class InboundShipmentItem(InboundShipmentItemBase):
    id: int
    inbound_shipment_id: int
    created_at: datetime

    class Config:
        from_attributes = True
