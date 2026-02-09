from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, func, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class PurchaseOrderStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    vendor = relationship("Vendor")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")
