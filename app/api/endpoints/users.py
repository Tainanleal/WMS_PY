from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core import models, schemas, security
from app.api import deps

router = APIRouter()

# --- Current User Actions ---

@router.post("/users/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Allows a logged-in user to change their own password.
    """
    current_user.hashed_password = security.get_password_hash(password_data.new_password)
    db.add(current_user)
    db.commit()
    return {"message": "Password updated successfully"}

# --- Admin-only User Management ---

@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Creates a new user and associates them with branches. Admin only.
    """
    if deps.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_data = user_in.dict()
    branch_ids = user_data.pop('branch_ids', None)
    password = user_data.pop('password')

    hashed_password = security.get_password_hash(password)
    new_user = models.User(**user_data, hashed_password=hashed_password)

    if branch_ids:
        branches = db.query(models.Branch).filter(models.Branch.id.in_(branch_ids)).all()
        if len(branches) != len(set(branch_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="One or more branches not found"
            )
        new_user.branches = branches

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Lists all users with their branch associations. Admin only.
    """
    users = db.query(models.User).options(joinedload(models.User.branches)).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Gets a specific user by ID with branch associations. Admin only.
    """
    user = db.query(models.User).options(joinedload(models.User.branches)).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Updates a user's info, including branch associations. Admin only.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.dict(exclude_unset=True)

    if 'branch_ids' in update_data:
        branch_ids = update_data.pop('branch_ids')
        if branch_ids is not None:
            branches = db.query(models.Branch).filter(models.Branch.id.in_(branch_ids)).all()
            if len(branches) != len(set(branch_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="One or more branches not found"
                )
            user.branches = branches
        else:
            user.branches = []

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
