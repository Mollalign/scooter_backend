"""Ride lifecycle, per-ride event log and high-volume GPS telemetry."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RideEndReason, RideEventType, RideStatus
from app.models.base import Base, TimestampMixin, UUIDMixin


class Ride(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "rides"

    ride_number: Mapped[str] = mapped_column(String(24), unique=True, nullable=False, index=True)

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    reservation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="SET NULL"),
    )

    status: Mapped[str] = mapped_column(
        String(16), default=RideStatus.ACTIVE.value, nullable=False, index=True,
    )

    # ─── Pricing snapshot (copied from the plan at unlock time) ────
    pricing_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pricing_plans.id", ondelete="SET NULL"),
    )
    currency: Mapped[str] = mapped_column(String(3), default="ETB", nullable=False)
    unlock_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    per_minute_rate: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    pause_rate_per_minute: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    minimum_charge: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    daily_cap: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # ─── Timings ───────────────────────────────────────────────────
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    paused_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ─── Locations ─────────────────────────────────────────────────
    start_location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    end_location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    path: Mapped[object | None] = mapped_column(
        Geography(geometry_type="LINESTRING", srid=4326)
    )
    distance_km: Mapped[float] = mapped_column(Numeric(8, 3), default=0, nullable=False)
    top_speed_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))

    # ─── Fare ──────────────────────────────────────────────────────
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    amount_charged: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    amount_owed: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    promo_code_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("promo_codes.id", ondelete="SET NULL"),
    )

    # ─── Ending metadata ───────────────────────────────────────────
    end_reason: Mapped[str | None] = mapped_column(String(24))
    ended_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
    end_location_outside_service: Mapped[bool] = mapped_column(default=False, nullable=False)
    battery_at_start: Mapped[int | None] = mapped_column(Integer)
    battery_at_end: Mapped[int | None] = mapped_column(Integer)

    events: Mapped[list["RideEvent"]] = relationship(
        back_populates="ride", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in RideStatus)})",
            name="ck_rides_status",
        ),
        CheckConstraint(
            f"end_reason IS NULL OR end_reason IN "
            f"({', '.join(repr(r.value) for r in RideEndReason)})",
            name="ck_rides_end_reason",
        ),
        CheckConstraint("duration_seconds >= 0", name="ck_rides_duration_nonneg"),
        CheckConstraint("total_cost >= 0", name="ck_rides_total_nonneg"),
    )


class RideEvent(UUIDMixin, TimestampMixin, Base):
    """Append-only ride state/event log for forensics & support."""

    __tablename__ = "ride_events"

    ride_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)

    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )

    ride: Mapped[Ride] = relationship(back_populates="events")

    __table_args__ = (
        CheckConstraint(
            f"event_type IN ({', '.join(repr(e.value) for e in RideEventType)})",
            name="ck_ride_events_type",
        ),
    )


class RidePing(Base):
    """
    High-volume GPS telemetry. Recommended: native partition by `created_at`
    monthly (hash or range). Kept lightweight for fast ingest.
    """

    __tablename__ = "ride_pings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False,
    )
    ride_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
    )
    location: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False,
    )
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))
    heading_deg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    battery_percent: Mapped[int | None] = mapped_column(Integer)
    accuracy_m: Mapped[float | None] = mapped_column(Numeric(6, 2))
