from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.schemas.user import UserResponse
from app.models.user import User
from app.core.enums import UserRole
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_active_user)):
    """Retrieves current authenticated user details."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves user profile details by ID (Self or Admin only)."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot access another user's profile",
        )

    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    if not user:
        raise NotFoundError("User", user_id)
    return user


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    """Lists registered users (Admin only)."""
    stmt = select(User).offset(skip).limit(limit)
    return db.scalars(stmt).all()
