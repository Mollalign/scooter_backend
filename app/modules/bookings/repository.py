from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingEvent


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        await self.db.flush()
        return booking

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        result = await self.db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> Booking | None:
        result = await self.db.execute(
            select(Booking).where(Booking.idempotency_key == key)
        )
        return result.scalar_one_or_none()

    async def get_customer_bookings(self, customer_id: UUID) -> list[Booking]:
        result = await self.db.execute(
            select(Booking)
            .where(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owner_bookings(self, owner_id: UUID) -> list[Booking]:
        result = await self.db.execute(
            select(Booking)
            .where(Booking.owner_id == owner_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_expired_pending_bookings(self) -> list[Booking]:
        from datetime import datetime, timezone

        result = await self.db.execute(
            select(Booking).where(
                Booking.status == "pending_payment",
                Booking.hold_expires_at < datetime.now(timezone.utc),
            )
        )
        return list(result.scalars().all())

    async def add_event(self, event: BookingEvent) -> BookingEvent:
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_events(self, booking_id: UUID) -> list[BookingEvent]:
        result = await self.db.execute(
            select(BookingEvent)
            .where(BookingEvent.booking_id == booking_id)
            .order_by(BookingEvent.created_at.asc())
        )
        return list(result.scalars().all())
