"""Wallet endpoints — balance, top-up, history, withdrawals."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.wallet.schemas import (
    TopupInitIn, TopupInitOut, WalletOut, WalletTransactionOut, WithdrawalIn, WithdrawalOut,
)
from app.api.v1.wallet.service import WalletService
from app.core.deps import get_current_verified_customer, get_db
from app.models.customer import Customer

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> WalletService:
    return WalletService(db)


@router.get("", response_model=WalletOut)
async def get_wallet(
    current: Customer = Depends(get_current_verified_customer),
    svc: WalletService = Depends(_service),
):
    return await svc.get_wallet(current)


@router.post("/topup", response_model=TopupInitOut, status_code=status.HTTP_201_CREATED)
async def init_topup(
    data: TopupInitIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: WalletService = Depends(_service),
):
    return await svc.init_topup(current, data)


@router.get("/transactions", response_model=list[WalletTransactionOut])
async def list_transactions(
    limit: int = Query(50, ge=1, le=100),
    cursor: str | None = Query(None),
    current: Customer = Depends(get_current_verified_customer),
    svc: WalletService = Depends(_service),
):
    return await svc.list_transactions(current, limit=limit, cursor=cursor)


@router.post("/withdrawals", response_model=WithdrawalOut, status_code=status.HTTP_201_CREATED)
async def request_withdrawal(
    data: WithdrawalIn,
    current: Customer = Depends(get_current_verified_customer),
    svc: WalletService = Depends(_service),
):
    return await svc.request_withdrawal(current, data)
