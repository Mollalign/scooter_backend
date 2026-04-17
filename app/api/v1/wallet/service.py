"""Wallet service: Chapa top-up, transaction history, withdrawals."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.wallet.schemas import TopupInitIn, TopupInitOut, WithdrawalIn
from app.models.customer import Customer


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_wallet(self, customer: Customer):
        raise NotImplementedError

    async def init_topup(self, customer: Customer, data: TopupInitIn) -> TopupInitOut:
        raise NotImplementedError

    async def list_transactions(
        self, customer: Customer, *, limit: int = 50, cursor: str | None = None,
    ):
        raise NotImplementedError

    async def request_withdrawal(self, customer: Customer, data: WithdrawalIn):
        raise NotImplementedError
