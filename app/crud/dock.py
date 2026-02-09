from sqlalchemy.orm import Session

from app.models.dock import Dock
from app.schemas.dock import DockCreate, DockUpdate


def get_dock(db: Session, dock_id: int) -> Dock:
    return db.query(Dock).filter(Dock.id == dock_id).first()


def get_docks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Dock).offset(skip).limit(limit).all()


def create_dock(db: Session, dock: DockCreate) -> Dock:
    db_dock = Dock(
        name=dock.name,
        dock_type=dock.dock_type,
    )
    db.add(db_dock)
    db.commit()
    db.refresh(db_dock)
    return db_dock


def update_dock(db: Session, dock_id: int, dock: DockUpdate) -> Dock:
    db_dock = get_dock(db, dock_id)
    if db_dock:
        db_dock.name = dock.name
        db_dock.dock_type = dock.dock_type
        db.commit()
        db.refresh(db_dock)
    return db_dock


def delete_dock(db: Session, dock_id: int) -> Dock:
    db_dock = get_dock(db, dock_id)
    if db_dock:
        db.delete(db_dock)
        db.commit()
    return db_dock
