from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

@router.put("/quality/stock_lots/{lot_id}", response_model=schemas.StockLot)
def update_stock_lot_status(
    lot_id: int,
    lot_update: schemas.StockLotUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Update the status of a stock lot (e.g., for quality inspection).
    - Moves a lot from PENDING to AVAILABLE or QUARANTINED.
    - Restricted to SUPERVISOR and ADMIN profiles.
    """
    # 1. Check user profile for authorization
    if current_user.profile not in [models.UserProfile.ADMIN, models.UserProfile.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to perform quality inspection."
        )

    # 2. Find the stock lot
    db_stock_lot = db.query(models.StockLot).filter(models.StockLot.id == lot_id).first()

    if not db_stock_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock lot not found")

    # 3. Check for branch access
    deps.check_branch_access(current_user, db_stock_lot.branch_id)

    # 4. Validate the status transition (optional but good practice)
    if db_stock_lot.status != models.StockLotStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from '{db_stock_lot.status}'. Only PENDING lots can be inspected."
        )
    
    if lot_update.status not in [models.StockLotStatus.AVAILABLE, models.StockLotStatus.QUARANTINED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target status. Must be AVAILABLE or QUARANTINED."
        )

    # 5. Update the lot
    db_stock_lot.status = lot_update.status
    db_stock_lot.inspected_at = func.now() # Use database time

    if lot_update.quantity is not None:
        db_stock_lot.quantity = lot_update.quantity

    db.commit()
    db.refresh(db_stock_lot)
    return db_stock_lot

@router.get("/quality/stock_lots/pending", response_model=List[schemas.StockLot])
def get_pending_stock_lots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get a list of all stock lots currently in PENDING status.
    - Useful for a quality inspection dashboard.
    - Admins see all pending lots.
    - Supervisors/Operators see lots from their assigned branches.
    """
    query = db.query(models.StockLot).filter(models.StockLot.status == models.StockLotStatus.PENDING).options(
        joinedload(models.StockLot.product),
        joinedload(models.StockLot.branch),
        joinedload(models.StockLot.created_by_user)
    )

    if current_user.profile != models.UserProfile.ADMIN:
        user_branch_ids = {branch.id for branch in current_user.branches}
        if not user_branch_ids:
            return []
        query = query.filter(models.StockLot.branch_id.in_(user_branch_ids))
    
    lots = query.order_by(models.StockLot.created_at.asc()).offset(skip).limit(limit).all()
    return lots
