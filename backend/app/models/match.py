import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import MatchStatus


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False
    )
    donor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    is_compatible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(MatchStatus), default=MatchStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    request: Mapped["BloodRequest"] = relationship("BloodRequest", back_populates="matches")
    donor: Mapped["DonorProfile"] = relationship("DonorProfile", back_populates="matches")
