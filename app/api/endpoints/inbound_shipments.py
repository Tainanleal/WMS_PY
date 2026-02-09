from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.inbound_shipment import InboundShipment, InboundShipmentCreate, InboundShipmentUpdate

router = APIRouter()


@router.get("/", response_model=List[InboundShipment])
def read_inbound_shipments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[InboundShipment]:
    """Retrieve inbound shipments."""
    shipments = crud.inbound_shipment.get_inbound_shipments(db, skip=skip, limit=limit)
    return shipments


@router.post("/", response_model=InboundShipment)
def create_inbound_shipment(
    *, 
    db: Session = Depends(deps.get_db), 
    shipment_in: InboundShipmentCreate
) -> InboundShipment:
    """Create new inbound shipment."""
    shipment = crud.inbound_shipment.create_inbound_shipment(db=db, shipment=shipment_in)
    return shipment


@router.get("/{shipment_id}", response_model=InboundShipment)
def read_inbound_shipment(
    shipment_id: int,
    db: Session = Depends(deps.get_db),
) -> InboundShipment:
    """Get inbound shipment by ID."""
    db_shipment = crud.inbound_shipment.get_inbound_shipment(db, shipment_id=shipment_id)
    if db_shipment is None:
        raise HTTPException(status_code=404, detail="Inbound shipment not found")
    return db_shipment


@router.put("/{shipment_id}", response_model=InboundShipment)
def update_inbound_shipment(
    *,
    db: Session = Depends(deps.get_db),
    shipment_id: int,
    shipment_in: InboundShipmentUpdate,
) -> InboundShipment:
    """Update an inbound shipment."""
    db_shipment = crud.inbound_shipment.get_inbound_shipment(db, shipment_id=shipment_id)
    if not db_shipment:
        raise HTTPException(status_code=404, detail="Inbound shipment not found")
    shipment = crud.inbound_shipment.update_inbound_shipment(
        db=db, shipment_id=shipment_id, shipment=shipment_in
    )
    return shipment


@router.delete("/{shipment_id}", response_model=InboundShipment)
def delete_inbound_shipment(
    shipment_id: int,
    db: Session = Depends(deps.get_db),
) -> InboundShipment:
    """Delete an inbound shipment."""
    db_shipment = crud.inbound_shipment.get_inbound_shipment(db, shipment_id=shipment_id)
    if not db_shipment:
        raise HTTPException(status_code=404, detail="Inbound shipment not found")
    shipment = crud.inbound_shipment.delete_inbound_shipment(db=db, shipment_id=shipment_id)
    return shipment
