from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import BloodGroup, UrgencyLevel, RequestStatus


class BloodRequestBase(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=100, example="Priya Verma")
    blood_group: BloodGroup
    units_needed: int = Field(1, ge=1, le=20, example=2)
    urgency: UrgencyLevel = UrgencyLevel.URGENT
    hospital_name: str = Field(..., min_length=3, max_length=255, example="AIIMS New Delhi, Ward 5")
    city: str = Field(..., min_length=2, max_length=100, example="Delhi")
    latitude: float = Field(..., ge=-90.0, le=90.0, example=28.5672)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=77.2100)
    additional_notes: str | None = None


class BloodRequestCreate(BloodRequestBase):
    requester_id: str | None = None


class BloodRequestUpdate(BaseModel):
    patient_name: str | None = None
    blood_group: BloodGroup | None = None
    units_needed: int | None = Field(None, ge=1, le=20)
    urgency: UrgencyLevel | None = None
    status: RequestStatus | None = None
    hospital_name: str | None = None
    city: str | None = None
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    additional_notes: str | None = None


class BloodRequestResponse(BloodRequestBase):
    id: str
    requester_id: str
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
