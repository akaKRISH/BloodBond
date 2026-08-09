import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.core.enums import UserRole


PHONE_REGEX = re.compile(r"^(\+91[\-\s]?)?[6-9]\d{9}$")


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Arjun Sharma")
    email: EmailStr = Field(..., example="arjun@example.com")
    phone: str = Field(..., example="+919876543210")
    role: UserRole = UserRole.BOTH

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean_phone = v.replace(" ", "").replace("-", "")
        if not PHONE_REGEX.match(clean_phone):
            raise ValueError("Phone number must be a valid 10-digit Indian phone number (optionally with +91 prefix)")
        return clean_phone


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    role: UserRole | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        clean_phone = v.replace(" ", "").replace("-", "")
        if not PHONE_REGEX.match(clean_phone):
            raise ValueError("Phone number must be a valid 10-digit Indian phone number")
        return clean_phone


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
