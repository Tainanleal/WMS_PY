import enum
from sqlalchemy import (
    Boolean, Column, Integer, String, ForeignKey, Enum, Table, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# --- Enums for Statuses and Roles ---

class UserProfile(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"

class StockLotStatus(str, enum.Enum):
    PENDING = "pending"      # Waiting for quality inspection
    AVAILABLE = "available"  # In stock, ready for use
    QUARANTINED = "quarantined" # Failed inspection, not for use

# --- Association Table for User-Branch Many-to-Many relationship ---
user_branch_association = Table(
    'user_branch_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('branch_id', Integer, ForeignKey('branches.id'), primary_key=True)
)

# --- Main Data Models ---

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=True)

    # Relationships
    users = relationship("User", secondary=user_branch_association, back_populates="branches")
    products = relationship("Product", back_populates="branch")
    stock_lots = relationship("StockLot", back_populates="branch")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # Relationships
    branch = relationship("Branch", back_populates="products")
    stock_lots = relationship("StockLot", back_populates="product")
    # Note: The direct relationship to inbound/outbound orders is removed
    # as all inventory movements will be tracked via StockLots.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    profile = Column(Enum(UserProfile), default=UserProfile.OPERATOR, nullable=False)

    # Relationships
    branches = relationship("Branch", secondary=user_branch_association, back_populates="users")
    created_stock_lots = relationship("StockLot", back_populates="created_by_user")

class InboundOrder(Base):
    __tablename__ = "inbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Relationships
    # This order will now generate one or more stock lots
    stock_lots = relationship("StockLot", back_populates="inbound_order")


class StockLot(Base):
    __tablename__ = "stock_lots"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    inbound_order_id = Column(Integer, ForeignKey("inbound_orders.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(StockLotStatus), nullable=False, default=StockLotStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    inspected_at = Column(DateTime(timezone=True), nullable=True)
    
    created_by_user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    product = relationship("Product", back_populates="stock_lots")
    branch = relationship("Branch", back_populates="stock_lots")
    inbound_order = relationship("InboundOrder", back_populates="stock_lots")
    created_by_user = relationship("User", back_populates="created_stock_lots")


class OutboundOrder(Base):
    __tablename__ = "outbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id")) # Still needed to know what was ordered
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # Note: The relationship between OutboundOrder and StockLot is more complex.
    # An outbound order might consume from multiple lots. This will be handled
    # in the business logic layer, potentially with an association table later.
