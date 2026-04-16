from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WalletBalanceResponse(BaseModel):
    owner_id: UUID
    balance: float
    currency: str = "ETB"


class LedgerEntryResponse(BaseModel):
    id: UUID
    booking_id: UUID | None
    entry_type: str
    amount: float
    direction: str
    balance_after: float
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PayoutRequestSchema(BaseModel):
    amount: float = Field(..., gt=0)
    payout_method: str = Field(..., pattern="^(telebirr|cbe_birr|bank_transfer)$")
