"""
Customer wallet system.

* `CustomerWallet`       — cached per-customer balance (one row per customer).
* `WalletTransaction`    — append-only double-entry ledger (never update, never delete).
* `ChapaTopup`           — Chapa checkout session linked to one (optional) WalletTransaction.
* `PaymentWebhookEvent`  — raw log of Chapa webhook payloads (dedup + audit).
* `Withdrawal`           — manual cash-out request requiring ops approval.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import (
    ChapaPaymentMethod, ChapaTopupStatus, LedgerDirection, WalletTxType,
    WebhookProcessingStatus, WithdrawalMethod, WithdrawalStatus,
)
from app.models.base import Base, TimestampMixin, UUIDMixin


class CustomerWallet(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customer_wallets"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="ETB", nullable=False)

    # Cached balance — authoritative reference is the ledger sum.
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    held_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    lifetime_topups: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    lifetime_spent: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_wallet_balance_nonneg"),
    )


class WalletTransaction(UUIDMixin, TimestampMixin, Base):
    """Every monetary movement on a customer wallet. Append-only."""

    __tablename__ = "wallet_transactions"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_wallets.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    tx_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Source references (exactly one is set depending on tx_type)
    ride_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rides.id", ondelete="SET NULL"), index=True,
    )
    topup_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapa_topups.id", ondelete="SET NULL"), index=True,
    )
    withdrawal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("withdrawals.id", ondelete="SET NULL"),
    )
    promo_redemption_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("promo_redemptions.id", ondelete="SET NULL"),
    )
    adjusted_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )

    reference: Mapped[str | None] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), unique=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_wallet_tx_amount_positive"),
        CheckConstraint(
            f"tx_type IN ({', '.join(repr(t.value) for t in WalletTxType)})",
            name="ck_wallet_tx_type",
        ),
        CheckConstraint(
            f"direction IN ({', '.join(repr(d.value) for d in LedgerDirection)})",
            name="ck_wallet_tx_direction",
        ),
    )


class ChapaTopup(UUIDMixin, TimestampMixin, Base):
    """One Chapa checkout session. Idempotent via `tx_ref`."""

    __tablename__ = "chapa_topups"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    tx_ref: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    chapa_ref: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ETB", nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(16))

    status: Mapped[str] = mapped_column(
        String(16), default=ChapaTopupStatus.INITIATED.value, nullable=False, index=True,
    )
    checkout_url: Mapped[str | None] = mapped_column(String(500))
    initialized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)

    raw_init_response: Mapped[dict | None] = mapped_column(JSON)
    raw_verify_response: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_chapa_topups_amount_positive"),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in ChapaTopupStatus)})",
            name="ck_chapa_topups_status",
        ),
        CheckConstraint(
            f"payment_method IS NULL OR payment_method IN "
            f"({', '.join(repr(m.value) for m in ChapaPaymentMethod)})",
            name="ck_chapa_topups_method",
        ),
    )


class PaymentWebhookEvent(UUIDMixin, TimestampMixin, Base):
    """Raw log of every webhook Chapa sends. Dedup via `event_id`."""

    __tablename__ = "payment_webhook_events"

    provider: Mapped[str] = mapped_column(String(16), default="chapa", nullable=False)
    event_id: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)
    tx_ref: Mapped[str | None] = mapped_column(String(64), index=True)

    signature_valid: Mapped[bool] = mapped_column(default=False, nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(16), default=WebhookProcessingStatus.RECEIVED.value, nullable=False, index=True,
    )
    processing_error: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    raw_headers: Mapped[dict | None] = mapped_column(JSON)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f"processing_status IN ({', '.join(repr(s.value) for s in WebhookProcessingStatus)})",
            name="ck_webhook_events_status",
        ),
    )


class Withdrawal(UUIDMixin, TimestampMixin, Base):
    """Customer request to move balance out of the wallet. Ops-approved."""

    __tablename__ = "withdrawals"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(24), nullable=False)
    account_details: Mapped[dict] = mapped_column(JSON, nullable=False)

    status: Mapped[str] = mapped_column(
        String(16), default=WithdrawalStatus.PENDING.value, nullable=False, index=True,
    )
    processed_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_withdrawals_amount_positive"),
        CheckConstraint(
            f"method IN ({', '.join(repr(m.value) for m in WithdrawalMethod)})",
            name="ck_withdrawals_method",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in WithdrawalStatus)})",
            name="ck_withdrawals_status",
        ),
    )
