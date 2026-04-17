"""Internal users — field operators, fleet managers, admins."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import StaffRole, StaffStatus
from app.models.base import Base, TimestampMixin, UUIDMixin


class Staff(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "staff"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(16), default=StaffStatus.ACTIVE.value, nullable=False, index=True
    )

    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f"role IN ({', '.join(repr(r.value) for r in StaffRole)})",
            name="ck_staff_role",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in StaffStatus)})",
            name="ck_staff_status",
        ),
    )
