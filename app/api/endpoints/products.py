from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Product)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(deps.get_db),
):
    """
    Create new product.
    """
    db_product = crud.get_product_by_sku(db, sku=product_in.sku)
    if db_product:
        raise HTTPException(status_code=400, detail="SKU already registered")
    return crud.create_product(db=db, product=product_in)


@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    """
    Retrieve products.
    """
    products = crud.get_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get product by ID.
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(deps.get_db),
):
    """
    Update a product.
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.update_product(db=db, product_id=product_id, product=product_in)
    return product


@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Deactivate a product (soft delete).
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Note: The CRUD function handles the soft delete logic.
    product = crud.delete_product(db=db, product_id=product_id)
    return product
