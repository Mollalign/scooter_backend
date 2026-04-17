"""Configurable pricing plans applied to scooters."""

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class PricingPlan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pricing_plans"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    currency: Mapped[str] = mapped_column(String(3), default="ETB", nullable=False)

    unlock_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    per_minute_rate: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    per_km_rate: Mapped[float | None] = mapped_column(Numeric(10, 2))
    pause_rate_per_minute: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    reservation_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    minimum_charge: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    daily_cap: Mapped[float | None] = mapped_column(Numeric(10, 2))

    free_minutes_per_ride: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    grace_seconds_before_unlock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
