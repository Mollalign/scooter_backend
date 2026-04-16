import logging

from app.core.constants import BookingStatus
from app.core.database import AsyncSessionLocal
from app.models.booking import BookingEvent
from app.modules.bookings.repository import BookingRepository

logger = logging.getLogger(__name__)


async def expire_pending_bookings():
    async with AsyncSessionLocal() as db:
        try:
            repo = BookingRepository(db)
            expired_bookings = await repo.get_expired_pending_bookings()

            for booking in expired_bookings:
                booking.status = BookingStatus.EXPIRED

                event = BookingEvent(
                    booking_id=booking.id,
                    event_type="booking_expired",
                    from_status=BookingStatus.PENDING_PAYMENT,
                    to_status=BookingStatus.EXPIRED,
                    actor_type="system",
                )
                db.add(event)

            if expired_bookings:
                await db.commit()
                logger.info(f"Expired {len(expired_bookings)} pending bookings")
        except Exception:
            logger.exception("Error in booking expiry job")
            await db.rollback()
