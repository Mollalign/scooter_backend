"""Short-term holds on a specific scooter for a customer."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReservationStatus
from app.models.base import Base, TimestampMixin, UUIDMixin


class Reservation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reservations"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    status: Mapped[str] = mapped_column(
        String(16), default=ReservationStatus.ACTIVE.value, nullable=False, index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    fee_charged: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in ReservationStatus)})",
            name="ck_reservations_status",
        ),
        # Only one active reservation per scooter at a time.
        UniqueConstraint("scooter_id", "status", name="uq_reservations_scooter_status"),
    )
