"""Customer (rider) identity, verification documents, OTP records."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    CustomerStatus, DocumentStatus, DocumentType, Language, OTPPurpose,
)
from app.models.base import Base, TimestampMixin, UUIDMixin


class Customer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    full_name: Mapped[str | None] = mapped_column(String(120))
    fan: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    preferred_language: Mapped[str] = mapped_column(String(8), default=Language.ENGLISH.value)

    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_document_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[str] = mapped_column(
        String(24), default=CustomerStatus.ACTIVE.value, nullable=False, index=True,
    )

    total_rides: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    documents: Mapped[list["CustomerDocument"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in CustomerStatus)})",
            name="ck_customers_status",
        ),
    )


class CustomerDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customer_documents"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default=DocumentStatus.PENDING.value, nullable=False, index=True,
    )
    reviewed_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(String(500))

    customer: Mapped[Customer] = relationship(back_populates="documents")

    __table_args__ = (
        CheckConstraint(
            f"document_type IN ({', '.join(repr(d.value) for d in DocumentType)})",
            name="ck_customer_documents_type",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in DocumentStatus)})",
            name="ck_customer_documents_status",
        ),
    )


class OTPVerification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "otp_verifications"

    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(String(24), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f"purpose IN ({', '.join(repr(p.value) for p in OTPPurpose)})",
            name="ck_otp_verifications_purpose",
        ),
        UniqueConstraint("phone", "purpose", "created_at", name="uq_otp_phone_purpose_created"),
    )
