from pydantic import BaseModel
from app.models.dock import DockType

# Shared properties
class DockBase(BaseModel):
    name: str
    dock_type: DockType

# Properties to receive on dock creation
class DockCreate(DockBase):
    pass

# Properties to receive on dock update
class DockUpdate(DockBase):
    pass

# Properties shared by models stored in DB
class DockInDBBase(DockBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client
class Dock(DockInDBBase):
    pass

# Properties stored in DB
class DockInDB(DockInDBBase):
    pass
