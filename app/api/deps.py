from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core import models, schemas, security
from app.core.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Database Dependency ---

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication & Authorization Dependencies ---

def get_user_by_email(db: Session, email: str):
    """Helper to get user from database."""
    return db.query(models.User).filter(models.User.email == email).first()

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """
    Decodes the JWT token to get the current user.
    Raises credentials exception if token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Gets the current user and checks if they are active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Gets the current active user and checks if they are an ADMIN.
    Raises an exception if the user is not an admin.
    """
    if current_user.profile != models.UserProfile.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_user

# --- Branch Access Dependency ---

def check_branch_access(user: models.User, branch_id: int):
    """
    Checks if a user has access to a specific branch.
    - Admins have access to all branches.
    - Other users must be explicitly assigned to the branch.
    """
    if user.profile == models.UserProfile.ADMIN:
        return True
    
    user_branch_ids = {branch.id for branch in user.branches}
    if branch_id not in user_branch_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this branch's resources."
        )
    return True
