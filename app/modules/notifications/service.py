from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.modules.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)

    async def send_sms(self, user_id: UUID, event_type: str, body: str, language: str = "am") -> Notification:
        notification = Notification(
            user_id=user_id,
            channel="sms",
            event_type=event_type,
            body=body,
            language=language,
            status="pending",
        )
        notification = await self.repo.create(notification)

        # TODO: call SMS gateway client, update status to sent/failed
        await self.db.commit()
        return notification

    async def send_push(self, user_id: UUID, event_type: str, title: str, body: str, language: str = "am") -> Notification:
        notification = Notification(
            user_id=user_id,
            channel="push",
            event_type=event_type,
            title=title,
            body=body,
            language=language,
            status="pending",
        )
        notification = await self.repo.create(notification)

        # TODO: call FCM client, update status to sent/failed
        await self.db.commit()
        return notification

    async def notify_booking_confirmed(self, customer_id: UUID, owner_id: UUID, booking_number: str) -> None:
        body = f"Booking {booking_number} confirmed successfully."
        await self.send_sms(customer_id, "booking_confirmed", body)
        await self.send_sms(owner_id, "booking_confirmed", f"New booking {booking_number} received.")
        await self.send_push(customer_id, "booking_confirmed", "Booking Confirmed", body)
        await self.send_push(owner_id, "booking_confirmed", "New Booking", f"New booking {booking_number} received.")
