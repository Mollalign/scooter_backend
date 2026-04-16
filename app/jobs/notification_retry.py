import logging

from app.core.database import AsyncSessionLocal
from app.modules.notifications.repository import NotificationRepository

logger = logging.getLogger(__name__)


async def retry_failed_notifications():
    async with AsyncSessionLocal() as db:
        try:
            repo = NotificationRepository(db)
            failed = await repo.get_failed_notifications(limit=20)

            for notification in failed:
                # TODO: retry sending via SMS or push based on notification.channel
                logger.info(f"Retrying notification {notification.id} on channel {notification.channel}")

            if failed:
                await db.commit()
        except Exception:
            logger.exception("Error in notification retry job")
            await db.rollback()
