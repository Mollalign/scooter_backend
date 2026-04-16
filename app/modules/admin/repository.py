from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AdminAuditLog
from app.models.wallet import Payout


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(self, log: AdminAuditLog) -> AdminAuditLog:
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_pending_payouts(self) -> list[Payout]:
        result = await self.db.execute(
            select(Payout)
            .where(Payout.status == "pending")
            .order_by(Payout.requested_at.asc())
        )
        return list(result.scalars().all())

    async def get_payout_by_id(self, payout_id: UUID) -> Payout | None:
        result = await self.db.execute(select(Payout).where(Payout.id == payout_id))
        return result.scalar_one_or_none()
