from pydantic import BaseModel
from typing import Optional

# --- Base Schema ---
class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

# --- Schema for Creating a Purchase Order Item ---
class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

# --- Schema for Updating a Purchase Order Item ---
class PurchaseOrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

# --- Schema for Reading/Returning a Purchase Order Item ---
class PurchaseOrderItem(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int

    class Config:
        from_attributes = True
