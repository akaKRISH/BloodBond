from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.donor import DonorProfile
from app.schemas.donor import DonorCreate, DonorUpdate
from app.core.errors import NotFoundError


class DonorService:
    @staticmethod
    def create_donor(db: Session, donor_in: DonorCreate) -> DonorProfile:
        donor = DonorProfile(**donor_in.model_dump())
        db.add(donor)
        db.commit()
        db.refresh(donor)
        return donor

    @staticmethod
    def get_by_id(db: Session, donor_id: str) -> DonorProfile:
        stmt = select(DonorProfile).where(DonorProfile.id == donor_id)
        donor = db.scalar(stmt)
        if not donor:
            raise NotFoundError("DonorProfile", donor_id)
        return donor

    @staticmethod
    def get_by_user_id(db: Session, user_id: str) -> DonorProfile | None:
        stmt = select(DonorProfile).where(DonorProfile.user_id == user_id)
        return db.scalar(stmt)

    @staticmethod
    def list_donors(
        db: Session,
        city: str | None = None,
        blood_group: str | None = None,
        is_available: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[DonorProfile]:
        stmt = select(DonorProfile)
        if city:
            stmt = stmt.where(DonorProfile.city.ilike(f"%{city}%"))
        if blood_group:
            stmt = stmt.where(DonorProfile.blood_group == blood_group)
        if is_available is not None:
            stmt = stmt.where(DonorProfile.is_available == is_available)
        stmt = stmt.offset(skip).limit(limit)
        return db.scalars(stmt).all()

    @staticmethod
    def update_availability(db: Session, donor_id: str, is_available: bool) -> DonorProfile:
        donor = DonorService.get_by_id(db, donor_id)
        donor.is_available = is_available
        db.commit()
        db.refresh(donor)
        return donor
