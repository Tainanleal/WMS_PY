from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

# --- Helper Function to Check Branch Access ---

def check_branch_access(user: models.User, branch_id: int):
    """Checks if a user has access to a specific branch."""
    if user.profile == models.UserProfile.ADMIN:
        return True # Admins have access to all branches
    
    user_branch_ids = {branch.id for branch in user.branches}
    if branch_id not in user_branch_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this branch."
        )
    return True

# --- CRUD for Products with Branch Governance ---

@router.post("/products/", response_model=schemas.Product)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Creates a new product in a specific branch.
    The user must be a member of the branch to create a product in it.
    """
    # 1. Check if branch exists
    branch = db.query(models.Branch).filter(models.Branch.id == product_in.branch_id).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    # 2. Check if the user has access to this branch
    check_branch_access(current_user, product_in.branch_id)

    # 3. Create the product
    new_product = models.Product(**product_in.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Lists products.
    - Admins see all products.
    - Other users see only products from their assigned branches.
    """
    query = db.query(models.Product).options(joinedload(models.Product.branch))

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return [] # Return empty list if user has no branches
        query = query.filter(models.Product.branch_id.in_(user_branch_ids))
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Gets a specific product by ID, checking for branch access.
    """
    product = db.query(models.Product).options(joinedload(models.Product.branch)).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    check_branch_access(current_user, product.branch_id)
    
    return product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Updates a product's details, checking for branch access.
    Note: Changing a product's branch is not allowed via this endpoint.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    check_branch_access(current_user, product.branch_id)

    update_data = product_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Deletes a product, checking for branch access.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    check_branch_access(current_user, product.branch_id)
    
    db.delete(product)
    db.commit()
    return
