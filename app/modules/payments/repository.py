from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentWebhookEvent, Refund


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def get_by_tx_ref(self, tx_ref: str) -> Payment | None:
        result = await self.db.execute(select(Payment).where(Payment.tx_ref == tx_ref))
        return result.scalar_one_or_none()

    async def get_by_booking_id(self, booking_id: UUID) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_payments_for_verification(self) -> list[Payment]:
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
        result = await self.db.execute(
            select(Payment).where(
                Payment.status == "pending",
                Payment.created_at < cutoff,
            )
        )
        return list(result.scalars().all())

    async def save_webhook_event(self, event: PaymentWebhookEvent) -> PaymentWebhookEvent:
        self.db.add(event)
        await self.db.flush()
        return event

    async def create_refund(self, refund: Refund) -> Refund:
        self.db.add(refund)
        await self.db.flush()
        return refund
