from .user import router as user_router
from .prescription import router as prescription_router
from fastapi import APIRouter


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(prescription_router, prefix="/prescriptions", tags=["prescriptions"])