from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import OwnerWalletLedger, Payout


class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_balance(self, owner_id: UUID) -> float:
        result = await self.db.execute(
            select(OwnerWalletLedger.balance_after)
            .where(OwnerWalletLedger.owner_id == owner_id)
            .order_by(OwnerWalletLedger.created_at.desc())
            .limit(1)
        )
        balance = result.scalar_one_or_none()
        return float(balance) if balance is not None else 0.0

    async def get_ledger_history(self, owner_id: UUID, limit: int = 50) -> list[OwnerWalletLedger]:
        result = await self.db.execute(
            select(OwnerWalletLedger)
            .where(OwnerWalletLedger.owner_id == owner_id)
            .order_by(OwnerWalletLedger.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_entry(self, entry: OwnerWalletLedger) -> OwnerWalletLedger:
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def create_payout(self, payout: Payout) -> Payout:
        self.db.add(payout)
        await self.db.flush()
        return payout

    async def get_owner_payouts(self, owner_id: UUID) -> list[Payout]:
        result = await self.db.execute(
            select(Payout)
            .where(Payout.owner_id == owner_id)
            .order_by(Payout.requested_at.desc())
        )
        return list(result.scalars().all())
