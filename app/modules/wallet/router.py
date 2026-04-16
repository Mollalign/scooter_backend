from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_owner
from app.models.user import User
from app.modules.wallet.schemas import (
    LedgerEntryResponse,
    PayoutRequestSchema,
    WalletBalanceResponse,
)
from app.modules.wallet.service import WalletService

router = APIRouter()


@router.get("/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)
    balance = await service.get_balance(owner)
    return WalletBalanceResponse(owner_id=owner.id, balance=balance)


@router.get("/history", response_model=list[LedgerEntryResponse])
async def get_wallet_history(
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)
    return await service.get_history(owner)


@router.post("/payout-request", status_code=201)
async def request_payout(
    data: PayoutRequestSchema,
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)
    payout = await service.request_payout(owner, data)
    return {"message": "Payout request submitted", "payout_id": str(payout.id)}
