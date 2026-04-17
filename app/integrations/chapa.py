"""
Chapa payment gateway client.

Docs: https://developer.chapa.co/docs/accept-payments
"""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ChapaIntegrationError

logger = logging.getLogger(__name__)


class ChapaClient:
    def __init__(self) -> None:
        self._base_url = settings.CHAPA_BASE_URL.rstrip("/")
        self._secret = settings.CHAPA_SECRET_KEY
        self._timeout = 20.0

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._secret}",
            "Content-Type": "application/json",
        }

    async def initialize(
        self,
        *,
        tx_ref: str,
        amount: float,
        email: str | None,
        phone: str,
        first_name: str | None,
        last_name: str | None,
        callback_url: str | None = None,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": "ETB",
            "email": email or "",
            "phone_number": phone,
            "first_name": first_name or "",
            "last_name": last_name or "",
            "callback_url": callback_url or settings.CHAPA_WEBHOOK_URL,
            "return_url": return_url or settings.CHAPA_CALLBACK_URL,
        }
        return await self._post("/transaction/initialize", payload)

    async def verify(self, tx_ref: str) -> dict[str, Any]:
        return await self._get(f"/transaction/verify/{tx_ref}")

    async def _post(self, path: str, json: dict) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                r = await client.post(
                    self._base_url + path, headers=self._headers, json=json,
                )
                r.raise_for_status()
                return r.json()
            except httpx.HTTPError as exc:
                logger.exception("Chapa POST %s failed", path)
                raise ChapaIntegrationError(str(exc)) from exc

    async def _get(self, path: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                r = await client.get(self._base_url + path, headers=self._headers)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPError as exc:
                logger.exception("Chapa GET %s failed", path)
                raise ChapaIntegrationError(str(exc)) from exc


def verify_signature(raw_body: bytes, signature: str | None) -> bool:
    """HMAC-SHA256 check of Chapa webhook body against `CHAPA_WEBHOOK_SECRET`."""
    import hashlib
    import hmac

    if not signature or not settings.CHAPA_WEBHOOK_SECRET:
        return False
    expected = hmac.new(
        settings.CHAPA_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
