import enum
from sqlalchemy import Column, Integer, String, Enum
from app.db.base_class import Base

class DockType(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

class Dock(Base):
    __tablename__ = "docks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    dock_type = Column(Enum(DockType), nullable=False)
