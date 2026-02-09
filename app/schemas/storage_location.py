from pydantic import BaseModel
from typing import Optional

# Shared properties
class StorageLocationBase(BaseModel):
    name: str
    location_type: str  # RACK, BIN, FLOOR
    branch_id: int
    dock_id: Optional[int] = None

# Properties to receive on item creation
class StorageLocationCreate(StorageLocationBase):
    pass

# Properties to receive on item update
class StorageLocationUpdate(StorageLocationBase):
    pass

# Properties shared by models stored in DB
class StorageLocationInDBBase(StorageLocationBase):
    id: int

    class Config:
        from_attributes = True

# Properties to return to client
class StorageLocation(StorageLocationInDBBase):
    pass

# Properties stored in DB
class StorageLocationInDB(StorageLocationInDBBase):
    pass
