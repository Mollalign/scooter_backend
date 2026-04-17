"""Customer scooter discovery — nearby + scan-by-code."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.scooters.schemas import ScooterDetailOut, ScooterMapOut
from app.api.v1.scooters.service import ScooterService
from app.core.deps import get_current_verified_customer, get_db

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> ScooterService:
    return ScooterService(db)


@router.get("/nearby", response_model=list[ScooterMapOut])
async def nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(1500, ge=50, le=10_000),
    vehicle_type: str | None = Query(None),
    _=Depends(get_current_verified_customer),
    svc: ScooterService = Depends(_service),
):
    return await svc.list_nearby(
        lat=lat, lng=lng, radius_m=radius_m, vehicle_type=vehicle_type,
    )


@router.get("/{identifier}", response_model=ScooterDetailOut)
async def get_scooter(
    identifier: str,
    _=Depends(get_current_verified_customer),
    svc: ScooterService = Depends(_service),
):
    """Look up a scooter by its displayed code (GF-123) or QR token."""
    return await svc.get_by_code_or_qr(identifier)
