"""Promotion codes and per-customer redemption records."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PromoKind
from app.models.base import Base, TimestampMixin, UUIDMixin


class PromoCode(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "promo_codes"

    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)

    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    value_numeric: Mapped[float | None] = mapped_column(Numeric(12, 2))

    max_total_redemptions: Mapped[int | None] = mapped_column(Integer)
    max_per_customer: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    min_wallet_balance: Mapped[float | None] = mapped_column(Numeric(12, 2))

    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )

    __table_args__ = (
        CheckConstraint(
            f"kind IN ({', '.join(repr(k.value) for k in PromoKind)})",
            name="ck_promo_codes_kind",
        ),
    )


class PromoRedemption(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "promo_redemptions"

    promo_code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promo_codes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    ride_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rides.id", ondelete="SET NULL"),
    )

    value_applied: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "promo_code_id", "customer_id", "ride_id",
            name="uq_promo_redemptions_per_ride",
        ),
    )
