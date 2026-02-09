from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.purchase_order import PurchaseOrderStatus
from .purchase_order_item import PurchaseOrderItem

# --- Base Schema ---
class PurchaseOrderBase(BaseModel):
    vendor_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: PurchaseOrderStatus = PurchaseOrderStatus.PENDING

# --- Schema for Creating a Purchase Order ---
class PurchaseOrderCreate(PurchaseOrderBase):
    pass

# --- Schema for Updating a Purchase Order ---
class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: Optional[date] = None
    status: Optional[PurchaseOrderStatus] = None

# --- Schema for Reading/Returning a Purchase Order ---
class PurchaseOrder(PurchaseOrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseOrderItem] = []

    class Config:
        from_attributes = True
