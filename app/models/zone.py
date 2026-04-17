"""Parking zones and dynamic geofence polygons."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import GeofenceType
from app.models.base import Base, TimestampMixin, UUIDMixin


class ParkingZone(UUIDMixin, TimestampMixin, Base):
    """A named logical grouping of scooters (e.g. 'Bole', 'Piassa')."""

    __tablename__ = "parking_zones"

    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Representative pin on the map (for list previews)
    center: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    # Optional boundary polygon for "pick from this zone" logic
    boundary: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326)
    )

    capacity: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class GeofenceZone(UUIDMixin, TimestampMixin, Base):
    """Dynamic zones: service area, no-parking, slow-speed, no-ride."""

    __tablename__ = "geofence_zones"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    polygon: Mapped[object] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326), nullable=False
    )

    # Slow-speed zones
    speed_limit_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))

    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL")
    )

    __table_args__ = (
        CheckConstraint(
            f"zone_type IN ({', '.join(repr(z.value) for z in GeofenceType)})",
            name="ck_geofence_zones_type",
        ),
    )
