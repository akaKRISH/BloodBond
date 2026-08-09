from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.core.enums import BloodGroup


class DonorBase(BaseModel):
    blood_group: BloodGroup
    city: str = Field(..., min_length=2, max_length=100, example="Delhi")
    latitude: float = Field(..., ge=-90.0, le=90.0, example=28.6139)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=77.2090)
    is_available: bool = True
    last_donation_date: date | None = None


class DonorCreate(DonorBase):
    user_id: str | None = None


class DonorUpdate(BaseModel):
    blood_group: BloodGroup | None = None
    city: str | None = None
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    is_available: bool | None = None
    last_donation_date: date | None = None


class DonorResponse(DonorBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Direct DTO matching index.html frontend object format
class FrontendDonorDTO(BaseModel):
    name: str
    city: str
    bt: str
    avail: bool
    lastDonated: str
    initials: str

    model_config = ConfigDict(from_attributes=True)
