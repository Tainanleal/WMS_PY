from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

@router.post("/outbound/orders", response_model=schemas.OutboundOrder)
def create_outbound_order(
    order_in: schemas.OutboundOrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Creates an outbound order, consuming stock from available lots using FIFO.
    """
    deps.check_branch_access(current_user, order_in.branch_id)

    # 1. Verify the product exists in the branch
    db_product = db.query(models.Product).filter(
        models.Product.id == order_in.product_id, 
        models.Product.branch_id == order_in.branch_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found in branch")

    # 2. Check for sufficient AVAILABLE stock across all lots
    total_available = db.query(func.sum(models.StockLot.quantity)).filter(
        models.StockLot.product_id == order_in.product_id,
        models.StockLot.branch_id == order_in.branch_id,
        models.StockLot.status == models.StockLotStatus.AVAILABLE
    ).scalar() or 0

    if total_available < order_in.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for product '{db_product.name}'. Available: {total_available}, Requested: {order_in.quantity}",
        )

    # 3. FIFO Picking Logic: Get available lots, oldest first
    available_lots = db.query(models.StockLot).filter(
        models.StockLot.product_id == order_in.product_id,
        models.StockLot.branch_id == order_in.branch_id,
        models.StockLot.status == models.StockLotStatus.AVAILABLE
    ).order_by(models.StockLot.created_at.asc()).all()

    quantity_to_pick = order_in.quantity
    
    for lot in available_lots:
        if quantity_to_pick <= 0: break

        picked_from_this_lot = min(lot.quantity, quantity_to_pick)
        
        lot.quantity -= picked_from_this_lot
        quantity_to_pick -= picked_from_this_lot

        if lot.quantity == 0:
            db.delete(lot)
        else:
            db.add(lot) # Mark for update

    # 4. Create the outbound order record
    db_outbound_order = models.OutboundOrder(
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        user_id=current_user.id,
        branch_id=order_in.branch_id,
    )
    db.add(db_outbound_order)
    
    # 5. Commit all changes (lot updates/deletions and new outbound order)
    db.commit()
    db.refresh(db_outbound_order)
    
    # Note: The returned OutboundOrder will not list the consumed lots,
    # but the database state is now correct.
    return db_outbound_order

@router.get("/outbound/orders", response_model=List[schemas.OutboundOrder])
def read_outbound_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Retrieve outbound orders log."""
    query = db.query(models.OutboundOrder).options(
        joinedload(models.OutboundOrder.branch),
        joinedload(models.OutboundOrder.product),
        joinedload(models.OutboundOrder.user),
    )

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return []
        query = query.filter(models.OutboundOrder.branch_id.in_(user_branch_ids))

    orders = query.order_by(models.OutboundOrder.id.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/outbound/orders/{order_id}", response_model=schemas.OutboundOrder)
def read_outbound_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Retrieve a specific outbound order by ID."""
    order = db.query(models.OutboundOrder).options(
        joinedload(models.OutboundOrder.branch),
        joinedload(models.OutboundOrder.product),
        joinedload(models.OutboundOrder.user),
    ).filter(models.OutboundOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Outbound order not found")

    deps.check_branch_access(current_user, order.branch_id)
    return order
