from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.match import Match
from app.models.donor import DonorProfile
from app.models.request import BloodRequest
from app.services.blood_matching import get_compatible_donor_groups
from app.services.geo_distance import calculate_haversine_distance
from app.core.enums import MatchStatus, RequestStatus
from app.core.errors import NotFoundError


class MatchService:
    @staticmethod
    def generate_matches_for_request(
        db: Session,
        request_id: str,
        radius_km: float = 10.0,
    ) -> Sequence[Match]:
        # 1. Fetch target blood request
        stmt_req = select(BloodRequest).where(BloodRequest.id == request_id)
        req = db.scalar(stmt_req)
        if not req:
            raise NotFoundError("BloodRequest", request_id)

        # 2. Determine compatible donor blood groups
        compatible_donor_groups = get_compatible_donor_groups(req.blood_group.value)

        # 3. Query available donors with compatible blood groups
        stmt_donors = select(DonorProfile).where(
            DonorProfile.is_available == True,
            DonorProfile.blood_group.in_(list(compatible_donor_groups)),
        )
        donors = db.scalars(stmt_donors).all()

        matches: list[Match] = []
        for donor in donors:
            # Skip if donor is the requester
            if donor.user_id == req.requester_id:
                continue

            dist = calculate_haversine_distance(
                req.latitude, req.longitude, donor.latitude, donor.longitude
            )

            # Filter within specified geographic radius
            if dist <= radius_km:
                # Check if match already exists
                stmt_existing = select(Match).where(
                    Match.request_id == req.id,
                    Match.donor_id == donor.id,
                )
                existing_match = db.scalar(stmt_existing)

                if not existing_match:
                    match_record = Match(
                        request_id=req.id,
                        donor_id=donor.id,
                        distance_km=dist,
                        is_compatible=True,
                        status=MatchStatus.PENDING,
                    )
                    db.add(match_record)
                    matches.append(match_record)
                else:
                    matches.append(existing_match)

        db.commit()

        # Update request status to MATCHED if matches were found
        if matches and req.status == RequestStatus.OPEN:
            req.status = RequestStatus.MATCHED
            db.commit()

        # Return matches sorted by distance
        stmt_result = (
            select(Match)
            .where(Match.request_id == req.id)
            .order_by(Match.distance_km.asc())
        )
        return db.scalars(stmt_result).all()

    @staticmethod
    def get_matches_by_request(db: Session, request_id: str) -> Sequence[Match]:
        stmt = select(Match).where(Match.request_id == request_id).order_by(Match.distance_km.asc())
        return db.scalars(stmt).all()

    @staticmethod
    def update_match_status(db: Session, match_id: str, status: MatchStatus) -> Match:
        stmt = select(Match).where(Match.id == match_id)
        match_obj = db.scalar(stmt)
        if not match_obj:
            raise NotFoundError("Match", match_id)
        match_obj.status = status
        db.commit()
        db.refresh(match_obj)
        return match_obj
