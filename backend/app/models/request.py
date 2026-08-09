import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Enum as SQLEnum, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import BloodGroup, UrgencyLevel, RequestStatus


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    requester_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    blood_group: Mapped[BloodGroup] = mapped_column(
        SQLEnum(BloodGroup), index=True, nullable=False
    )
    units_needed: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    urgency: Mapped[UrgencyLevel] = mapped_column(
        SQLEnum(UrgencyLevel), default=UrgencyLevel.URGENT, index=True, nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus), default=RequestStatus.OPEN, index=True, nullable=False
    )
    hospital_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    requester: Mapped["User"] = relationship("User", back_populates="requests")
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="request", cascade="all, delete-orphan"
    )
