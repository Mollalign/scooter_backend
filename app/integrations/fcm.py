"""Firebase Cloud Messaging client (stub)."""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class FCMClient:
    async def send_to_token(
        self, *, token: str, title: str, body: str, data: dict[str, Any] | None = None,
    ) -> dict:
        if not settings.FCM_SERVER_KEY:
            logger.info("[FCM disabled] token=%s title=%s", token[:12], title)
            return {"mocked": True}
        # TODO: use firebase-admin SDK in production
        raise NotImplementedError("Wire firebase-admin here")
