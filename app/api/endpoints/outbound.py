from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

@router.post("/outbound/orders", response_model=schemas.OutboundOrder)
def create_outbound_order(
    order_in: schemas.OutboundOrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Create a new outbound order from a specific branch.
    - The user must belong to the specified branch.
    - The product must exist in the same branch.
    - Checks for sufficient stock before processing.
    """
    # 1. Check branch access
    deps.check_branch_access(current_user, order_in.branch_id)

    # 2. Verify the product exists in the same branch
    db_product = db.query(models.Product).filter(
        models.Product.id == order_in.product_id,
        models.Product.branch_id == order_in.branch_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found in the specified branch"
        )

    # 3. Check for sufficient stock
    if db_product.quantity < order_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product '{db_product.name}'. Available: {db_product.quantity}, Requested: {order_in.quantity}"
        )

    # 4. Create the outbound order and update product quantity
    db_outbound_order = models.OutboundOrder(
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        user_id=current_user.id,
        branch_id=order_in.branch_id
    )
    
    db_product.quantity -= order_in.quantity
    
    db.add(db_outbound_order)
    db.add(db_product)
    db.commit()
    db.refresh(db_outbound_order)
    
    return db_outbound_order

@router.get("/outbound/orders", response_model=List[schemas.OutboundOrder])
def read_outbound_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve outbound orders.
    - Admins see all orders.
    - Other users see only orders from their assigned branches.
    """
    query = db.query(models.OutboundOrder).options(
        joinedload(models.OutboundOrder.branch),
        joinedload(models.OutboundOrder.product),
        joinedload(models.OutboundOrder.user)
    )

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return [] # No branches, no orders
        query = query.filter(models.OutboundOrder.branch_id.in_(user_branch_ids))

    orders = query.order_by(models.OutboundOrder.id.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/outbound/orders/{order_id}", response_model=schemas.OutboundOrder)
def read_outbound_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve a specific outbound order by ID, checking for branch access.
    """
    order = db.query(models.OutboundOrder).options(
        joinedload(models.OutboundOrder.branch),
        joinedload(models.OutboundOrder.product),
        joinedload(models.OutboundOrder.user)
    ).filter(models.OutboundOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outbound order not found")

    # Check access
    deps.check_branch_access(current_user, order.branch_id)

    return order
