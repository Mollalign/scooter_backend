"""Webhook dispatcher — validates signatures and reconciles payments."""

from sqlalchemy.ext.asyncio import AsyncSession


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_chapa(self, *, raw_body: bytes, signature: str | None) -> None:
        """Verify signature → persist event → apply wallet credit → idempotent."""
        raise NotImplementedError
