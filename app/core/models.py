import enum
from sqlalchemy import (
    Boolean, Column, Integer, String, ForeignKey, Enum, Table
)
from sqlalchemy.orm import relationship
from .database import Base

# Define the user profiles/roles
class UserProfile(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"

# --- Association Table for User-Branch Many-to-Many relationship ---
user_branch_association = Table(
    'user_branch_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('branch_id', Integer, ForeignKey('branches.id'), primary_key=True)
)


class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=True)

    # Relationship to Users (many-to-many)
    users = relationship(
        "User",
        secondary=user_branch_association,
        back_populates="branches"
    )

    # Relationships to other models (one-to-many)
    products = relationship("Product", back_populates="branch")
    inbound_orders = relationship("InboundOrder", back_populates="branch")
    outbound_orders = relationship("OutboundOrder", back_populates="branch")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    quantity = Column(Integer)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    branch = relationship("Branch", back_populates="products")
    inbound_orders = relationship("InboundOrder", back_populates="product")
    outbound_orders = relationship("OutboundOrder", back_populates="product")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    profile = Column(Enum(UserProfile), default=UserProfile.OPERATOR, nullable=False)

    # Relationships
    inbound_orders = relationship("InboundOrder", back_populates="user")
    outbound_orders = relationship("OutboundOrder", back_populates="user")
    branches = relationship(
        "Branch",
        secondary=user_branch_association,
        back_populates="users"
    )


class InboundOrder(Base):
    __tablename__ = "inbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    branch = relationship("Branch", back_populates="inbound_orders")
    product = relationship("Product", back_populates="inbound_orders")
    user = relationship("User", back_populates="inbound_orders")


class OutboundOrder(Base):
    __tablename__ = "outbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    branch = relationship("Branch", back_populates="outbound_orders")
    product = relationship("Product", back_populates="outbound_orders")
    user = relationship("User", back_populates="outbound_orders")
