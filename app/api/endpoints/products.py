from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

# --- Helper Function for Quantity Calculation ---

def _calculate_and_attach_quantities(db: Session, product: models.Product):
    """
    Calculates inventory quantities from StockLots and attaches them to a product object.
    The product object is modified in-place.
    """
    # Query for quantities grouped by status
    quantities = (
        db.query(
            models.StockLot.status,
            func.sum(models.StockLot.quantity).label("total_quantity"),
        )
        .filter(models.StockLot.product_id == product.id)
        .group_by(models.StockLot.status)
        .all()
    )

    # Initialize quantities on the Pydantic-mapped object
    product.quantity_available = 0
    product.quantity_pending = 0
    product.quantity_quarantined = 0

    # Assign calculated quantities
    for status, total_quantity in quantities:
        if status == models.StockLotStatus.AVAILABLE:
            product.quantity_available = total_quantity or 0
        elif status == models.StockLotStatus.PENDING:
            product.quantity_pending = total_quantity or 0
        elif status == models.StockLotStatus.QUARANTINED:
            product.quantity_quarantined = total_quantity or 0

# --- CRUD for Products with New Inventory Logic ---

@router.post("/products/", response_model=schemas.Product)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Creates a new product. Quantity is now managed via StockLots, not here.
    """
    deps.check_branch_access(current_user, product_in.branch_id)
    
    new_product = models.Product(**product_in.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Attach the (zero) quantities for the response model
    _calculate_and_attach_quantities(db, new_product)
    return new_product

@router.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Lists products with calculated inventory quantities from their stock lots.
    """
    query = db.query(models.Product).options(joinedload(models.Product.branch))

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return []
        query = query.filter(models.Product.branch_id.in_(user_branch_ids))

    products = query.order_by(models.Product.id).offset(skip).limit(limit).all()

    # For each product, calculate and attach its inventory quantities
    for product in products:
        _calculate_and_attach_quantities(db, product)

    return products

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Gets a specific product with calculated inventory quantities.
    """
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.branch))
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    deps.check_branch_access(current_user, product.branch_id)

    # Calculate and attach the inventory quantities before returning
    _calculate_and_attach_quantities(db, product)

    return product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Updates a product's details (name, description). Quantity cannot be updated here.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    deps.check_branch_access(current_user, db_product.branch_id)

    update_data = product_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Recalculate quantities for the response
    _calculate_and_attach_quantities(db, db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Deletes a product. Note: This could fail if stock lots reference it.
    Proper handling would archive the product instead.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    deps.check_branch_access(current_user, db_product.branch_id)

    # Check if there are any stock lots associated with the product
    has_lots = db.query(models.StockLot).filter(models.StockLot.product_id == product_id).first()
    if has_lots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete product with existing stock lots. Archive it instead."
        )

    db.delete(db_product)
    db.commit()
    return
