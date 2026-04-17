"""Ride lifecycle endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.rides.schemas import (
    EndRideIn, RideOut, RidePingIn, RideSummaryOut, UnlockIn,
)
from app.api.v1.rides.service import RideService
from app.core.deps import get_current_verified_customer, get_db
from app.models.customer import Customer

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> RideService:
    return RideService(db)


@router.post("/unlock", response_model=RideOut, status_code=status.HTTP_201_CREATED)
async def unlock(
    data: UnlockIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.unlock(current, data)


@router.get("/current", response_model=RideOut | None)
async def current(
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.get_current(current)


@router.post("/{ride_id}/pause", response_model=RideOut)
async def pause(
    ride_id: UUID,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.pause(current, ride_id)


@router.post("/{ride_id}/resume", response_model=RideOut)
async def resume(
    ride_id: UUID,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.resume(current, ride_id)


@router.post("/{ride_id}/end", response_model=RideOut)
async def end(
    ride_id: UUID,
    data: EndRideIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.end(current, ride_id, data)


@router.post("/{ride_id}/pings", status_code=status.HTTP_204_NO_CONTENT)
async def push_ping(
    ride_id: UUID,
    data: RidePingIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    await svc.record_ping(current, ride_id, data)


@router.get("/history", response_model=list[RideSummaryOut])
async def history(
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.list_history(current, limit=limit, cursor=cursor)


@router.get("/{ride_id}", response_model=RideOut)
async def get_ride(
    ride_id: UUID,
    current: Customer = Depends(get_current_verified_customer),
    svc: RideService = Depends(_service),
):
    return await svc.get(current, ride_id)
