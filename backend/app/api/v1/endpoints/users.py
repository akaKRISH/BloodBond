from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.core.errors import NotFoundError, AppException

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user on the platform."""
    # Check duplicate email or phone
    stmt_email = select(User).where(User.email == user_in.email)
    if db.scalar(stmt_email):
        raise AppException("Email address is already registered.", code="DUPLICATE_EMAIL")

    stmt_phone = select(User).where(User.phone == user_in.phone)
    if db.scalar(stmt_phone):
        raise AppException("Phone number is already registered.", code="DUPLICATE_PHONE")

    user = User(**user_in.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Retrieves user profile details by ID."""
    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    if not user:
        raise NotFoundError("User", user_id)
    return user


@router.get("", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lists registered users (admin/development endpoint)."""
    stmt = select(User).offset(skip).limit(limit)
    return db.scalars(stmt).all()
