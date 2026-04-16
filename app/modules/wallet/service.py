from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.user import User
from app.models.wallet import OwnerWalletLedger, Payout
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.schemas import PayoutRequestSchema


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WalletRepository(db)

    async def get_balance(self, owner: User) -> float:
        return await self.repo.get_balance(owner.id)

    async def get_history(self, owner: User) -> list[OwnerWalletLedger]:
        return await self.repo.get_ledger_history(owner.id)

    async def credit_earnings(self, owner_id: UUID, booking_id: UUID, amount: float) -> OwnerWalletLedger:
        current_balance = await self.repo.get_balance(owner_id)
        new_balance = round(current_balance + amount, 2)

        entry = OwnerWalletLedger(
            owner_id=owner_id,
            booking_id=booking_id,
            entry_type="earning_credit",
            amount=amount,
            direction="credit",
            balance_after=new_balance,
            description=f"Booking earnings credited",
        )
        entry = await self.repo.add_entry(entry)
        await self.db.commit()
        return entry

    async def request_payout(self, owner: User, data: PayoutRequestSchema) -> Payout:
        balance = await self.repo.get_balance(owner.id)
        if data.amount > balance:
            raise AppException("Insufficient balance for payout request")

        payout = Payout(
            owner_id=owner.id,
            amount=data.amount,
            status="pending",
            payout_method=data.payout_method,
        )
        payout = await self.repo.create_payout(payout)
        await self.db.commit()
        return payout
