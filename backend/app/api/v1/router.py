from fastapi import APIRouter
from app.api.v1.endpoints import users, donors, requests, matches

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(donors.router, prefix="/donors", tags=["Donors"])
api_router.include_router(requests.router, prefix="/requests", tags=["Requests"])
api_router.include_router(matches.router, prefix="", tags=["Matches"])
