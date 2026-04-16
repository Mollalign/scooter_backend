from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApproveScooterRequest(BaseModel):
    approved: bool
    rejection_reason: str | None = Field(None, max_length=500)


class VerifyUserDocumentRequest(BaseModel):
    approved: bool
    review_notes: str | None = Field(None, max_length=500)


class ProcessPayoutRequest(BaseModel):
    reference: str = Field(..., max_length=200)
    payout_method: str = Field(..., pattern="^(telebirr|cbe_birr|bank_transfer|manual)$")


class AuditLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    action: str
    target_type: str
    target_id: UUID
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
