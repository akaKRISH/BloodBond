from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status as http_status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_active_user
from app.schemas.request import BloodRequestCreate, BloodRequestResponse
from app.services.request_service import RequestService
from app.models.user import User
from app.core.enums import RequestStatus, UserRole
from app.core.errors import NotFoundError

router = APIRouter()


@router.post("", response_model=BloodRequestResponse, status_code=http_status.HTTP_201_CREATED)
def create_blood_request(
    request_in: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submits an urgent or scheduled blood request for the authenticated user."""
    if request_in.requester_id and request_in.requester_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot create a blood request for another user",
        )

    if not request_in.requester_id:
        request_in.requester_id = current_user.id

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
    current_user: User = Depends(get_current_active_user),
):
    """Updates the status of a blood request (Requester owner or Admin only)."""
    req = RequestService.get_by_id(db, request_id)
    if req.requester_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot modify another user's blood request",
        )
    return RequestService.update_status(db, request_id, status)
