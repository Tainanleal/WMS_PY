from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.core.models import UserProfile

# --- Base Schemas ---

class BranchBase(BaseModel):
    name: str
    location: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int
    branch_id: int  # Every product must belong to a branch

class UserBase(BaseModel):
    email: EmailStr

class InboundOrderBase(BaseModel):
    product_id: int
    quantity: int
    branch_id: int # Every order must belong to a branch

class OutboundOrderBase(BaseModel):
    product_id: int
    quantity: int
    branch_id: int # Every order must belong to a branch

# --- Create Schemas ---

class BranchCreate(BranchBase):
    pass

class ProductCreate(ProductBase):
    pass

class UserCreate(UserBase):
    password: str
    profile: UserProfile = UserProfile.OPERATOR
    branch_ids: Optional[List[int]] = None

class InboundOrderCreate(InboundOrderBase):
    pass

class OutboundOrderCreate(OutboundOrderBase):
    pass

# --- Update Schemas ---

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    # branch_id is typically not updatable, a product move would be a new transaction

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    profile: Optional[UserProfile] = None
    branch_ids: Optional[List[int]] = None

# --- Full Schemas (for API responses) ---

class Branch(BranchBase):
    id: int

    class Config:
        from_attributes = True

class Product(ProductBase):
    id: int
    branch: Branch # Nested branch details

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    profile: UserProfile
    branches: List[Branch] = []

    class Config:
        from_attributes = True

class InboundOrder(InboundOrderBase):
    id: int
    user_id: int
    branch: Branch
    product: Product
    user: User

    class Config:
        from_attributes = True

class OutboundOrder(OutboundOrderBase):
    id: int
    user_id: int
    branch: Branch
    product: Product
    user: User

    class Config:
        from_attributes = True

# --- Password & Token Schemas ---

class PasswordChange(BaseModel):
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
