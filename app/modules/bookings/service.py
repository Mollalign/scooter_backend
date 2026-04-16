from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import BookingStatus
from app.core.exceptions import AppException, BookingConflictException, ForbiddenException, NotFoundException
from app.models.booking import Booking, BookingEvent
from app.models.user import User
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.state_machine import validate_transition
from app.modules.scooters.repository import ScooterRepository
from app.utils.booking_number import generate_booking_number


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BookingRepository(db)
        self.scooter_repo = ScooterRepository(db)

    async def create_booking(self, customer: User, scooter_id: UUID, start_time: datetime, end_time: datetime, idempotency_key: str | None = None) -> Booking:
        if idempotency_key:
            existing = await self.repo.get_by_idempotency_key(idempotency_key)
            if existing:
                return existing

        scooter = await self.scooter_repo.get_by_id(scooter_id)
        if not scooter:
            raise NotFoundException("Scooter not found")
        if not scooter.is_approved or scooter.status != "available":
            raise AppException("Scooter is not available for booking")

        if end_time <= start_time:
            raise AppException("End time must be after start time")
        duration_hours = (end_time - start_time).total_seconds() / 3600
        if duration_hours < 1:
            raise AppException("Minimum rental duration is 1 hour")

        if duration_hours >= 24:
            days = duration_hours / 24
            total_amount = float(scooter.price_per_day) * days
        else:
            total_amount = float(scooter.price_per_hour) * duration_hours

        total_amount = round(total_amount, 2)
        platform_fee_rate = settings.PLATFORM_FEE_RATE
        platform_fee = round(total_amount * platform_fee_rate, 2)
        owner_earnings = round(total_amount - platform_fee, 2)

        booking = Booking(
            booking_number=generate_booking_number(),
            customer_id=customer.id,
            scooter_id=scooter.id,
            owner_id=scooter.owner_id,
            start_time=start_time,
            end_time=end_time,
            status=BookingStatus.PENDING_PAYMENT,
            total_amount=total_amount,
            platform_fee=platform_fee,
            platform_fee_rate=platform_fee_rate,
            owner_earnings=owner_earnings,
            hold_expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.BOOKING_HOLD_MINUTES),
            idempotency_key=idempotency_key,
        )

        try:
            booking = await self.repo.create(booking)
        except Exception:
            raise BookingConflictException()

        event = BookingEvent(
            booking_id=booking.id,
            event_type="booking_created",
            from_status=None,
            to_status=BookingStatus.PENDING_PAYMENT,
            actor_type="customer",
            actor_id=customer.id,
        )
        await self.repo.add_event(event)
        await self.db.commit()

        return booking

    async def cancel_booking(self, booking_id: UUID, user: User, reason: str | None = None) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")

        if booking.customer_id != user.id and booking.owner_id != user.id:
            raise ForbiddenException("You are not part of this booking")

        validate_transition(booking.status, BookingStatus.CANCELLED)

        old_status = booking.status
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
        booking.cancelled_by = user.id

        actor_type = "customer" if booking.customer_id == user.id else "owner"
        event = BookingEvent(
            booking_id=booking.id,
            event_type="booking_cancelled",
            from_status=old_status,
            to_status=BookingStatus.CANCELLED,
            actor_type=actor_type,
            actor_id=user.id,
            reason=reason,
        )
        await self.repo.add_event(event)
        await self.db.commit()

        # TODO: trigger refund logic based on cancellation policy
        return booking

    async def confirm_pickup(self, booking_id: UUID, owner: User) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        if booking.owner_id != owner.id:
            raise ForbiddenException("Only the scooter owner can confirm pickup")

        validate_transition(booking.status, BookingStatus.ACTIVE)

        booking.status = BookingStatus.ACTIVE
        booking.pickup_confirmed_at = datetime.now(timezone.utc)

        event = BookingEvent(
            booking_id=booking.id,
            event_type="pickup_confirmed",
            from_status=BookingStatus.CONFIRMED,
            to_status=BookingStatus.ACTIVE,
            actor_type="owner",
            actor_id=owner.id,
        )
        await self.repo.add_event(event)
        await self.db.commit()
        return booking

    async def confirm_return(self, booking_id: UUID, owner: User) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        if booking.owner_id != owner.id:
            raise ForbiddenException("Only the scooter owner can confirm return")

        validate_transition(booking.status, BookingStatus.COMPLETED)

        booking.status = BookingStatus.COMPLETED
        booking.return_confirmed_at = datetime.now(timezone.utc)

        event = BookingEvent(
            booking_id=booking.id,
            event_type="booking_completed",
            from_status=BookingStatus.ACTIVE,
            to_status=BookingStatus.COMPLETED,
            actor_type="owner",
            actor_id=owner.id,
        )
        await self.repo.add_event(event)

        # TODO: credit owner wallet ledger with owner_earnings

        await self.db.commit()
        return booking
