from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.inbound_shipment_item import (
    InboundShipmentItem,
    InboundShipmentItemCreate,
    InboundShipmentItemUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[InboundShipmentItem])
def read_inbound_shipment_items(
    shipment_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[InboundShipmentItem]:
    """Retrieve inbound shipment items for a specific shipment."""
    items = crud.inbound_shipment_item.get_inbound_shipment_items_by_shipment(
        db, shipment_id=shipment_id, skip=skip, limit=limit
    )
    return items


@router.post("/", response_model=InboundShipmentItem)
def create_inbound_shipment_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: InboundShipmentItemCreate,
) -> InboundShipmentItem:
    """Create a new inbound shipment item."""
    item = crud.inbound_shipment_item.create_inbound_shipment_item(db=db, item=item_in)
    return item


@router.get("/{item_id}", response_model=InboundShipmentItem)
def read_inbound_shipment_item(
    item_id: int,
    db: Session = Depends(deps.get_db),
) -> InboundShipmentItem:
    """Get inbound shipment item by ID."""
    db_item = crud.inbound_shipment_item.get_inbound_shipment_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Inbound shipment item not found")
    return db_item


@router.put("/{item_id}", response_model=InboundShipmentItem)
def update_inbound_shipment_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: InboundShipmentItemUpdate,
) -> InboundShipmentItem:
    """Update an inbound shipment item."""
    db_item = crud.inbound_shipment_item.get_inbound_shipment_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbound shipment item not found")
    item = crud.inbound_shipment_item.update_inbound_shipment_item(
        db=db, item_id=item_id, item=item_in
    )
    return item


@router.delete("/{item_id}", response_model=InboundShipmentItem)
def delete_inbound_shipment_item(
    item_id: int,
    db: Session = Depends(deps.get_db),
) -> InboundShipmentItem:
    """Delete an inbound shipment item."""
    db_item = crud.inbound_shipment_item.get_inbound_shipment_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbound shipment item not found")
    item = crud.inbound_shipment_item.delete_inbound_shipment_item(db=db, item_id=item_id)
    return item
