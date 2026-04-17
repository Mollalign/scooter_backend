"""SMS gateway client (stub — wire to AfroMessage, Twilio, etc.)."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSClient:
    async def send(self, *, phone: str, message: str) -> dict:
        if not settings.SMS_API_URL or not settings.SMS_API_KEY:
            logger.info("[SMS disabled] to=%s body=%s", phone, message)
            return {"mocked": True}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                settings.SMS_API_URL,
                headers={"Authorization": f"Bearer {settings.SMS_API_KEY}"},
                json={
                    "to": phone,
                    "from": settings.SMS_SENDER_NAME,
                    "message": message,
                },
            )
            resp.raise_for_status()
            return resp.json()
