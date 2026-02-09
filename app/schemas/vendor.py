from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Base Schema ---
class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone_number: Optional[str] = None

# --- Schema for Creating a Vendor ---
class VendorCreate(VendorBase):
    pass

# --- Schema for Updating a Vendor ---
class VendorUpdate(VendorBase):
    is_active: Optional[bool] = None

# --- Schema for Reading/Returning a Vendor ---
class Vendor(VendorBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
