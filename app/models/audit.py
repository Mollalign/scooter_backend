"""Admin audit log + system-wide configuration."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ActorType
from app.models.base import Base, TimestampMixin, UUIDMixin


class AdminAuditLog(UUIDMixin, TimestampMixin, Base):
    """Immutable record of every sensitive staff action."""

    __tablename__ = "admin_audit_logs"

    actor_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"), index=True,
    )

    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(40), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(64), index=True)

    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    context: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (
        CheckConstraint(
            f"actor_type IN ({', '.join(repr(a.value) for a in ActorType)})",
            name="ck_admin_audit_logs_actor",
        ),
    )


class SystemConfig(UUIDMixin, TimestampMixin, Base):
    """Runtime-tunable settings (pricing toggles, feature flags, messaging templates)."""

    __tablename__ = "system_configs"

    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    updated_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
