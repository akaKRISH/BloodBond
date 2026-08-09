from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.request import BloodRequest
from app.schemas.request import BloodRequestCreate, BloodRequestUpdate
from app.core.enums import RequestStatus
from app.core.errors import NotFoundError


class RequestService:
    @staticmethod
    def create_request(db: Session, request_in: BloodRequestCreate) -> BloodRequest:
        blood_request = BloodRequest(**request_in.model_dump())
        db.add(blood_request)
        db.commit()
        db.refresh(blood_request)
        return blood_request

    @staticmethod
    def get_by_id(db: Session, request_id: str) -> BloodRequest:
        stmt = select(BloodRequest).where(BloodRequest.id == request_id)
        req = db.scalar(stmt)
        if not req:
            raise NotFoundError("BloodRequest", request_id)
        return req

    @staticmethod
    def list_requests(
        db: Session,
        city: str | None = None,
        blood_group: str | None = None,
        status: RequestStatus | None = RequestStatus.OPEN,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[BloodRequest]:
        stmt = select(BloodRequest)
        if city:
            stmt = stmt.where(BloodRequest.city.ilike(f"%{city}%"))
        if blood_group:
            stmt = stmt.where(BloodRequest.blood_group == blood_group)
        if status:
            stmt = stmt.where(BloodRequest.status == status)
        stmt = stmt.order_by(BloodRequest.created_at.desc()).offset(skip).limit(limit)
        return db.scalars(stmt).all()

    @staticmethod
    def update_status(db: Session, request_id: str, status: RequestStatus) -> BloodRequest:
        req = RequestService.get_by_id(db, request_id)
        req.status = status
        db.commit()
        db.refresh(req)
        return req
