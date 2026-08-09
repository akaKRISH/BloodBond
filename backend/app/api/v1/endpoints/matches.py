from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.match import MatchResponse, MatchStatusUpdate
from app.services.match_service import MatchService
from app.core.enums import MatchStatus

router = APIRouter()


@router.post("/requests/{request_id}/match", response_model=List[MatchResponse])
def trigger_matching_engine(
    request_id: str,
    radius_km: float = Query(10.0, ge=1.0, le=500.0, description="Geographic radius search limit in km"),
    db: Session = Depends(get_db),
):
    """Executes blood compatibility matrix & Haversine geo-distance matching algorithm for a blood request."""
    return MatchService.generate_matches_for_request(db, request_id=request_id, radius_km=radius_km)


@router.get("/requests/{request_id}/matches", response_model=List[MatchResponse])
def get_matches_for_request(request_id: str, db: Session = Depends(get_db)):
    """Retrieves all matches computed for a given blood request."""
    return MatchService.get_matches_by_request(db, request_id=request_id)


@router.patch("/matches/{match_id}/status", response_model=MatchResponse)
def update_match_status(
    match_id: str,
    status_update: MatchStatusUpdate,
    db: Session = Depends(get_db),
):
    """Updates status of a donor match (ACCEPT, DECLINE, NOTIFY, COMPLETE)."""
    return MatchService.update_match_status(db, match_id=match_id, status=status_update.status)
