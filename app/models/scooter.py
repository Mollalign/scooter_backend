import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Scooter(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scooters"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    sub_city: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    location_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_per_hour: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_day: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unlisted")
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    owner: Mapped["User"] = relationship(back_populates="scooters", lazy="selectin")
    images: Mapped[list["ScooterImage"]] = relationship(
        back_populates="scooter", lazy="selectin", cascade="all, delete-orphan"
    )


class ScooterImage(Base, UUIDMixin):
    __tablename__ = "scooter_images"

    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scooters.id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )

    scooter: Mapped["Scooter"] = relationship(back_populates="images")


from app.models.user import User  # noqa: E402
