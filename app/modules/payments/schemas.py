from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentInitResponse(BaseModel):
    payment_id: UUID
    tx_ref: str
    checkout_url: str
    booking_id: UUID


class PaymentStatusResponse(BaseModel):
    payment_id: UUID
    booking_id: UUID
    status: str
    is_verified: bool
    amount: float
    payment_method: str | None
    paid_at: datetime | None

    model_config = {"from_attributes": True}


class WebhookPayload(BaseModel):
    """Raw Chapa webhook payload — fields vary; this captures the essentials."""
    tx_ref: str | None = None
    status: str | None = None
    amount: float | None = None
    currency: str | None = None
    reference: str | None = None

    model_config = {"extra": "allow"}
