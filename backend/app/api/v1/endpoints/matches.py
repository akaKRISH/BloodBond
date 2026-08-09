from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.match import MatchResponse, MatchStatusUpdate
from app.services.match_service import MatchService
from app.services.request_service import RequestService
from app.models.user import User
from app.core.enums import UserRole

router = APIRouter()


@router.post("/requests/{request_id}/match", response_model=List[MatchResponse])
def trigger_matching_engine(
    request_id: str,
    radius_km: float = Query(10.0, ge=1.0, le=500.0, description="Geographic radius search limit in km"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Executes blood compatibility matrix & Haversine geo-distance matching algorithm for a blood request."""
    req = RequestService.get_by_id(db, request_id)
    if req.requester_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot trigger matching for another user's request",
        )
    return MatchService.generate_matches_for_request(db, request_id=request_id, radius_km=radius_km)


@router.get("/requests/{request_id}/matches", response_model=List[MatchResponse])
def get_matches_for_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves all matches computed for a given blood request (Requester owner or Admin)."""
    req = RequestService.get_by_id(db, request_id)
    if req.requester_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot view matches for another user's request",
        )
    return MatchService.get_matches_by_request(db, request_id=request_id)


@router.patch("/matches/{match_id}/status", response_model=MatchResponse)
def update_match_status(
    match_id: str,
    status_update: MatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates status of a donor match (ACCEPT, DECLINE, NOTIFY, COMPLETE)."""
    return MatchService.update_match_status(db, match_id=match_id, status=status_update.status)
