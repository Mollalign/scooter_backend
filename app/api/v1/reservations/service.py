"""Reservation service — short-term hold on a scooter."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reservations.schemas import ReservationIn
from app.models.customer import Customer


class ReservationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, customer: Customer, data: ReservationIn):
        raise NotImplementedError

    async def cancel(self, customer: Customer, reservation_id: UUID) -> None:
        raise NotImplementedError

    async def get_current(self, customer: Customer):
        raise NotImplementedError
