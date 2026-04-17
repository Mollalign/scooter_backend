"""Push / SMS / in-app notifications queued for customers and staff."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ActorType, NotificationChannel, NotificationStatus
from app.models.base import Base, TimestampMixin, UUIDMixin


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    # Polymorphic recipient: exactly one of customer/staff is set
    recipient_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True,
    )
    staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), index=True,
    )

    channel: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(
        String(16), default=NotificationStatus.PENDING.value, nullable=False, index=True,
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(120))

    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            f"recipient_type IN ({repr(ActorType.CUSTOMER.value)}, {repr(ActorType.STAFF.value)})",
            name="ck_notifications_recipient_type",
        ),
        CheckConstraint(
            f"channel IN ({', '.join(repr(c.value) for c in NotificationChannel)})",
            name="ck_notifications_channel",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in NotificationStatus)})",
            name="ck_notifications_status",
        ),
    )
