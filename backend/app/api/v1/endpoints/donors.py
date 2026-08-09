from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.schemas.donor import DonorCreate, DonorResponse, FrontendDonorDTO
from app.services.donor_service import DonorService
from app.models.user import User
from app.core.errors import NotFoundError, AppException

router = APIRouter()


@router.post("", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor_profile(donor_in: DonorCreate, db: Session = Depends(get_db)):
    """Creates a new donor profile associated with a user."""
    # Verify user exists
    user = db.scalar(select(User).where(User.id == donor_in.user_id))
    if not user:
        raise NotFoundError("User", donor_in.user_id)

    # Verify user doesn't already have a donor profile
    existing = DonorService.get_by_user_id(db, donor_in.user_id)
    if existing:
        raise AppException("User already has an active donor profile.", code="DONOR_PROFILE_EXISTS")

    return DonorService.create_donor(db, donor_in)


@router.get("", response_model=List[DonorResponse])
def search_donors(
    city: Optional[str] = Query(None, description="Filter by city name"),
    blood_group: Optional[str] = Query(None, description="Filter by blood group (e.g., O+, A-)"),
    is_available: Optional[bool] = Query(None, description="Filter by availability status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Searches and filters active donors by location, blood type, and availability."""
    return DonorService.list_donors(
        db, city=city, blood_group=blood_group, is_available=is_available, skip=skip, limit=limit
    )


@router.get("/frontend-dto", response_model=List[FrontendDonorDTO])
def get_donors_frontend_format(db: Session = Depends(get_db)):
    """Returns donor network data formatted for direct consumption by index.html."""
    donors = DonorService.list_donors(db, is_available=True)
    dto_list = []
    for d in donors:
        user_name = d.user.name if d.user else "Anonymous Donor"
        initials = "".join([w[0] for w in user_name.split()]).upper()[:2]
        dto_list.append(
            FrontendDonorDTO(
                name=user_name,
                city=d.city,
                bt=d.blood_group.value,
                avail=d.is_available,
                lastDonated=str(d.last_donation_date) if d.last_donation_date else "Never",
                initials=initials or "BD",
            )
        )
    return dto_list


@router.get("/{donor_id}", response_model=DonorResponse)
def get_donor(donor_id: str, db: Session = Depends(get_db)):
    """Retrieves donor profile by ID."""
    return DonorService.get_by_id(db, donor_id)


@router.patch("/{donor_id}/availability", response_model=DonorResponse)
def toggle_availability(
    donor_id: str,
    is_available: bool = Query(..., description="Set availability flag"),
    db: Session = Depends(get_db),
):
    """Toggles donor availability status."""
    return DonorService.update_availability(db, donor_id, is_available)
