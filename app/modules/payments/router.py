import hmac
import hashlib
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.payments.schemas import PaymentStatusResponse
from app.modules.payments.service import PaymentService

router = APIRouter()


@router.post("/webhook")
async def chapa_webhook(
    request: Request,
    chapa_signature: str | None = Header(None, alias="Chapa-Signature"),
    db: AsyncSession = Depends(get_db),
):
    raw_body = await request.body()
    payload = await request.json()

    signature_valid = False
    if chapa_signature and settings.CHAPA_WEBHOOK_SECRET:
        expected = hmac.HMAC(
            settings.CHAPA_WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        signature_valid = hmac.compare_digest(expected, chapa_signature)

    tx_ref = payload.get("tx_ref") or payload.get("trx_ref", "")

    service = PaymentService(db)
    await service.process_webhook(tx_ref, payload, signature_valid)

    return {"status": "received"}


@router.get("/booking/{booking_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    payment = await service.get_payment_status(booking_id)
    return payment
