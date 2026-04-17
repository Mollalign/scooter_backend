"""
Ride service — state machine for the active ride.

    active → paused → active → ending → ended
                                       ↘ force_ended / lost_signal
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.rides.schemas import EndRideIn, RidePingIn, UnlockIn
from app.models.customer import Customer


class RideService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def unlock(self, customer: Customer, data: UnlockIn):
        """Validate → charge-hold → send IoT unlock → create Ride."""
        raise NotImplementedError

    async def get_current(self, customer: Customer):
        raise NotImplementedError

    async def pause(self, customer: Customer, ride_id: UUID):
        raise NotImplementedError

    async def resume(self, customer: Customer, ride_id: UUID):
        raise NotImplementedError

    async def end(self, customer: Customer, ride_id: UUID, data: EndRideIn):
        """Compute fare → charge wallet → send IoT lock → finalize ride."""
        raise NotImplementedError

    async def record_ping(self, customer: Customer, ride_id: UUID, data: RidePingIn) -> None:
        raise NotImplementedError

    async def list_history(self, customer: Customer, *, limit: int, cursor: str | None):
        raise NotImplementedError

    async def get(self, customer: Customer, ride_id: UUID):
        raise NotImplementedError
