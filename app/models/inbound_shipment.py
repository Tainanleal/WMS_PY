from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, func, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class InboundShipmentStatus(enum.Enum):
    EXPECTED = "EXPECTED"
    ARRIVED = "ARRIVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"

class InboundShipment(Base):
    __tablename__ = "inbound_shipments"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    arrival_date = Column(Date)
    status = Column(Enum(InboundShipmentStatus), default=InboundShipmentStatus.EXPECTED, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    purchase_order = relationship("PurchaseOrder")
    items = relationship("InboundShipmentItem", back_populates="inbound_shipment")
