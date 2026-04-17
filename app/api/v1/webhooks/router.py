"""Public webhook endpoints (signed)."""

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.webhooks.schemas import WebhookAck
from app.api.v1.webhooks.service import WebhookService
from app.core.deps import get_db

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> WebhookService:
    return WebhookService(db)


@router.post("/chapa", response_model=WebhookAck)
async def chapa_webhook(
    request: Request,
    chapa_signature: str | None = Header(default=None, alias="Chapa-Signature"),
    svc: WebhookService = Depends(_service),
):
    raw = await request.body()
    await svc.handle_chapa(raw_body=raw, signature=chapa_signature)
    return WebhookAck()
