from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

@router.post("/inbound/orders", response_model=schemas.InboundOrder)
def create_inbound_order(
    order_in: schemas.InboundOrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Create a new inbound order in a specific branch.
    - The user must belong to the specified branch.
    - The associated product must also belong to the same branch.
    """
    # 1. Check branch access
    deps.check_branch_access(current_user, order_in.branch_id)

    # 2. Verify the product exists and belongs to the same branch
    db_product = db.query(models.Product).filter(
        models.Product.id == order_in.product_id,
        models.Product.branch_id == order_in.branch_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found in the specified branch"
        )

    # 3. Create the inbound order and update product quantity
    db_inbound_order = models.InboundOrder(
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        user_id=current_user.id,
        branch_id=order_in.branch_id
    )
    
    db_product.quantity += order_in.quantity
    
    db.add(db_inbound_order)
    db.add(db_product)
    db.commit()
    db.refresh(db_inbound_order)
    
    return db_inbound_order

@router.get("/inbound/orders", response_model=List[schemas.InboundOrder])
def read_inbound_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve inbound orders.
    - Admins see all orders.
    - Other users see only orders from their assigned branches.
    """
    query = db.query(models.InboundOrder).options(
        joinedload(models.InboundOrder.branch),
        joinedload(models.InboundOrder.product),
        joinedload(models.InboundOrder.user)
    )

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return [] # No branches, no orders
        query = query.filter(models.InboundOrder.branch_id.in_(user_branch_ids))

    orders = query.order_by(models.InboundOrder.id.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/inbound/orders/{order_id}", response_model=schemas.InboundOrder)
def read_inbound_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve a specific inbound order by ID, checking for branch access.
    """
    order = db.query(models.InboundOrder).options(
        joinedload(models.InboundOrder.branch),
        joinedload(models.InboundOrder.product),
        joinedload(models.InboundOrder.user)
    ).filter(models.InboundOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inbound order not found")

    # Check access
    deps.check_branch_access(current_user, order.branch_id)

    return order
