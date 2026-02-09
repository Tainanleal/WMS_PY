from sqlalchemy import Column, Integer, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class InboundShipmentItem(Base):
    __tablename__ = "inbound_shipment_items"

    id = Column(Integer, primary_key=True, index=True)
    inbound_shipment_id = Column(Integer, ForeignKey("inbound_shipments.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_received = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    inbound_shipment = relationship("InboundShipment", back_populates="items")
    product = relationship("Product")
