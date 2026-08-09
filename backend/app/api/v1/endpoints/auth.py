from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.errors import AppException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user with hashed password."""
    # Check duplicate email
    stmt_email = select(User).where(User.email == user_in.email)
    if db.scalar(stmt_email):
        raise AppException("Email address is already registered.", code="DUPLICATE_EMAIL")

    # Check duplicate phone
    stmt_phone = select(User).where(User.phone == user_in.phone)
    if db.scalar(stmt_phone):
        raise AppException("Phone number is already registered.", code="DUPLICATE_PHONE")

    # Hash password
    pwd_hash = get_password_hash(user_in.password)

    user_dict = user_in.model_dump(exclude={"password"})
    user_dict["password_hash"] = pwd_hash

    user = User(**user_dict)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 compatible token login endpoint (expects username=email, password)."""
    stmt = select(User).where(User.email == form_data.username)
    user = db.scalar(stmt)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    return Token(access_token=token, token_type="bearer")


@router.post("/login/json", response_model=Token)
def login_json(
    login_in: UserLogin,
    db: Session = Depends(get_db),
):
    """JSON body login endpoint for web frontend clients."""
    stmt = select(User).where(User.email == login_in.email)
    user = db.scalar(stmt)

    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    return Token(access_token=token, token_type="bearer")
