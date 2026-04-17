"""Wallet / top-up / withdrawal schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: float
    held_amount: float
    currency: str


class TopupInitIn(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str | None = None


class TopupInitOut(BaseModel):
    topup_id: UUID
    tx_ref: str
    checkout_url: str
    amount: float


class WalletTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tx_type: str
    direction: str
    amount: float
    balance_after: float
    description: str | None
    created_at: datetime


class WithdrawalIn(BaseModel):
    amount: float = Field(..., gt=0)
    method: str
    account_details: dict


class WithdrawalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: float
    method: str
    status: str
    created_at: datetime
