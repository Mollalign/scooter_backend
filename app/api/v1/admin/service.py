"""Admin service — customer mgmt, fleet mgmt, pricing, payouts, dashboard."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin.schemas import PricingPlanIn, ScooterAdminIn


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Dashboard ─────────────────────────────────────────────
    async def dashboard(self):
        raise NotImplementedError

    # ── Customers ─────────────────────────────────────────────
    async def list_customers(self, *, q: str | None, limit: int, offset: int):
        raise NotImplementedError

    async def suspend_customer(self, customer_id: UUID, reason: str) -> None:
        raise NotImplementedError

    async def approve_document(self, document_id: UUID) -> None:
        raise NotImplementedError

    async def reject_document(self, document_id: UUID, reason: str) -> None:
        raise NotImplementedError

    # ── Scooters ─────────────────────────────────────────────
    async def create_scooter(self, data: ScooterAdminIn):
        raise NotImplementedError

    async def list_scooters(self, *, q: str | None, status: str | None, limit: int, offset: int):
        raise NotImplementedError

    # ── Pricing ──────────────────────────────────────────────
    async def create_pricing_plan(self, data: PricingPlanIn):
        raise NotImplementedError

    async def list_pricing_plans(self):
        raise NotImplementedError

    # ── Payouts ──────────────────────────────────────────────
    async def approve_withdrawal(self, withdrawal_id: UUID) -> None:
        raise NotImplementedError

    async def reject_withdrawal(self, withdrawal_id: UUID, reason: str) -> None:
        raise NotImplementedError
