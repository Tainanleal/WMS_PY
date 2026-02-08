from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core import models, schemas
from app.api import deps

router = APIRouter()

# --- CRUD for Branches ---

@router.post("/branches/", response_model=schemas.Branch, status_code=status.HTTP_201_CREATED)
def create_branch(
    branch_in: schemas.BranchCreate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Creates a new branch. Only accessible by admin users.
    """
    db_branch = db.query(models.Branch).filter(models.Branch.name == branch_in.name).first()
    if db_branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Branch name already exists",
        )
    new_branch = models.Branch(**branch_in.dict())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch

@router.get("/branches/", response_model=List[schemas.Branch])
def read_branches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user) # Any active user can see branches
):
    """
    Lists all branches.
    """
    branches = db.query(models.Branch).offset(skip).limit(limit).all()
    return branches

@router.get("/branches/{branch_id}", response_model=schemas.Branch)
def read_branch(
    branch_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Gets a specific branch by ID.
    """
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.put("/branches/{branch_id}", response_model=schemas.Branch)
def update_branch(
    branch_id: int,
    branch_in: schemas.BranchUpdate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Updates a branch. Only accessible by admin users.
    """
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = branch_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(branch, key, value)

    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch

@router.delete("/branches/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(
    branch_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Deletes a branch. Only accessible by admin users.
    """
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    db.delete(branch)
    db.commit()
    return 
