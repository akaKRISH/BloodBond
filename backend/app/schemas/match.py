from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import MatchStatus
from app.schemas.donor import DonorResponse


class MatchBase(BaseModel):
    request_id: str
    donor_id: str
    distance_km: float
    is_compatible: bool = True
    status: MatchStatus = MatchStatus.PENDING


class MatchCreate(MatchBase):
    pass


class MatchStatusUpdate(BaseModel):
    status: MatchStatus


class MatchResponse(MatchBase):
    id: str
    created_at: datetime
    donor: DonorResponse | None = None

    model_config = ConfigDict(from_attributes=True)
