"""Physical scooter/bike/moped fleet."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.core.enums import ScooterStatus, VehicleType
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.iot import IoTDevice


class Scooter(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "scooters"

    # Display code printed on vehicle ("GF-123", "BK-456")
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    qr_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    vehicle_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    model_name: Mapped[str | None] = mapped_column(String(80))
    serial_number: Mapped[str | None] = mapped_column(String(80), unique=True)

    status: Mapped[str] = mapped_column(
        String(24), default=ScooterStatus.INACTIVE.value, nullable=False, index=True,
    )

    # Live telemetry (kept denormalized on the row for fast map queries)
    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), index=True
    )
    heading_deg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))
    battery_percent: Mapped[int | None] = mapped_column(Integer)
    range_km: Mapped[float | None] = mapped_column(Numeric(6, 2))
    last_ping_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    is_locked: Mapped[bool] = mapped_column(default=True, nullable=False)

    parking_zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parking_zones.id", ondelete="SET NULL"), index=True,
    )
    pricing_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pricing_plans.id", ondelete="SET NULL"),
    )

    total_rides: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_distance_km: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    last_maintenance_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    iot_device: Mapped["IoTDevice"] = relationship(
        "IoTDevice", back_populates="scooter", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            f"vehicle_type IN ({', '.join(repr(v.value) for v in VehicleType)})",
            name="ck_scooters_vehicle_type",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in ScooterStatus)})",
            name="ck_scooters_status",
        ),
        CheckConstraint(
            "battery_percent IS NULL OR (battery_percent BETWEEN 0 AND 100)",
            name="ck_scooters_battery_range",
        ),
    )
