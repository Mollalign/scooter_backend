"""Reservation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reservations.schemas import ReservationIn, ReservationOut
from app.api.v1.reservations.service import ReservationService
from app.core.deps import get_current_verified_customer, get_db
from app.models.customer import Customer

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> ReservationService:
    return ReservationService(db)


@router.post("", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: ReservationService = Depends(_service),
):
    return await svc.create(current, data)


@router.get("/current", response_model=ReservationOut | None)
async def current_reservation(
    current: Customer = Depends(get_current_verified_customer),
    svc: ReservationService = Depends(_service),
):
    return await svc.get_current(current)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: UUID,
    current: Customer = Depends(get_current_verified_customer),
    svc: ReservationService = Depends(_service),
):
    await svc.cancel(current, reservation_id)
