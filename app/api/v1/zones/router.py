"""Public map data — parking zones and active geofences."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.zones.schemas import GeofenceZoneOut, ParkingZoneOut
from app.api.v1.zones.service import ZoneService
from app.core.deps import get_db

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> ZoneService:
    return ZoneService(db)


@router.get("/parking", response_model=list[ParkingZoneOut])
async def list_parking_zones(svc: ZoneService = Depends(_service)):
    return await svc.list_parking_zones()


@router.get("/geofences", response_model=list[GeofenceZoneOut])
async def list_geofences(
    zone_type: str | None = Query(None),
    svc: ZoneService = Depends(_service),
):
    return await svc.list_geofences(zone_type=zone_type)
