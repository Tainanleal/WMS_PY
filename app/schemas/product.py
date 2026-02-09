from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema for creating a product (input)
class ProductCreate(BaseModel):
    sku: str
    description: str

# Schema for updating a product (input)
class ProductUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for reading a product (output)
class Product(BaseModel):
    id: int
    sku: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
