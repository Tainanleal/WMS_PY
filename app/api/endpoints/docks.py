from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.dock import Dock, DockCreate, DockUpdate

router = APIRouter()


@router.get("/", response_model=List[Dock])
def read_docks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[Dock]:
    """Retrieve docks."""
    docks = crud.dock.get_docks(db, skip=skip, limit=limit)
    return docks


@router.post("/", response_model=Dock)
def create_dock(
    *,
    db: Session = Depends(deps.get_db),
    dock_in: DockCreate,
) -> Dock:
    """Create a new dock."""
    dock = crud.dock.create_dock(db=db, dock=dock_in)
    return dock


@router.get("/{dock_id}", response_model=Dock)
def read_dock(
    dock_id: int,
    db: Session = Depends(deps.get_db),
) -> Dock:
    """Get dock by ID."""
    db_dock = crud.dock.get_dock(db, dock_id=dock_id)
    if db_dock is None:
        raise HTTPException(status_code=404, detail="Dock not found")
    return db_dock


@router.put("/{dock_id}", response_model=Dock)
def update_dock(
    *,
    db: Session = Depends(deps.get_db),
    dock_id: int,
    dock_in: DockUpdate,
) -> Dock:
    """Update a dock."""
    db_dock = crud.dock.get_dock(db, dock_id=dock_id)
    if not db_dock:
        raise HTTPException(status_code=404, detail="Dock not found")
    dock = crud.dock.update_dock(db=db, dock_id=dock_id, dock=dock_in)
    return dock


@router.delete("/{dock_id}", response_model=Dock)
def delete_dock(
    dock_id: int,
    db: Session = Depends(deps.get_db),
) -> Dock:
    """Delete a dock."""
    db_dock = crud.dock.get_dock(db, dock_id=dock_id)
    if not db_dock:
        raise HTTPException(status_code=404, detail="Dock not found")
    dock = crud.dock.delete_dock(db=db, dock_id=dock_id)
    return dock
