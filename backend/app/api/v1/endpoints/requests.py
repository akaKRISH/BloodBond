from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.schemas.request import BloodRequestCreate, BloodRequestResponse
from app.services.request_service import RequestService
from app.models.user import User
from app.core.enums import RequestStatus
from app.core.errors import NotFoundError

router = APIRouter()


@router.post("", response_model=BloodRequestResponse, status_code=status.HTTP_201_CREATED)
def create_blood_request(request_in: BloodRequestCreate, db: Session = Depends(get_db)):
    """Submits an urgent or scheduled blood request."""
    # Verify user exists
    user = db.scalar(select(User).where(User.id == request_in.requester_id))
    if not user:
        raise NotFoundError("User", request_in.requester_id)

    return RequestService.create_request(db, request_in)


@router.get("", response_model=List[BloodRequestResponse])
def list_blood_requests(
    city: Optional[str] = Query(None, description="Filter by city"),
    blood_group: Optional[str] = Query(None, description="Filter by required blood group"),
    status: Optional[RequestStatus] = Query(RequestStatus.OPEN, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Lists active blood requests filtered by location, blood group, or status."""
    return RequestService.list_requests(
        db, city=city, blood_group=blood_group, status=status, skip=skip, limit=limit
    )


@router.get("/{request_id}", response_model=BloodRequestResponse)
def get_blood_request(request_id: str, db: Session = Depends(get_db)):
    """Retrieves blood request details by ID."""
    return RequestService.get_by_id(db, request_id)


@router.patch("/{request_id}/status", response_model=BloodRequestResponse)
def update_request_status(
    request_id: str,
    status: RequestStatus = Query(..., description="Target status (OPEN, MATCHED, FULFILLED, CANCELLED)"),
    db: Session = Depends(get_db),
):
    """Updates the status of a blood request."""
    return RequestService.update_status(db, request_id, status)
