"""Operational workflows: maintenance tasks, battery swaps, incidents."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import (
    IncidentSeverity, IncidentStatus, IncidentType, MaintenanceType,
    TaskPriority, TaskStatus,
)
from app.models.base import Base, TimestampMixin, UUIDMixin


class BatterySwapStation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "battery_swap_stations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False,
    )
    capacity: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MaintenanceTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "maintenance_tasks"

    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    task_type: Mapped[str] = mapped_column(String(24), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(16), default=TaskPriority.NORMAL.value, nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(16), default=TaskStatus.OPEN.value, nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    reported_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
    assigned_to_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"), index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion_notes: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[list | None] = mapped_column(JSON)

    __table_args__ = (
        CheckConstraint(
            f"task_type IN ({', '.join(repr(t.value) for t in MaintenanceType)})",
            name="ck_maintenance_tasks_type",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in TaskStatus)})",
            name="ck_maintenance_tasks_status",
        ),
        CheckConstraint(
            f"priority IN ({', '.join(repr(p.value) for p in TaskPriority)})",
            name="ck_maintenance_tasks_priority",
        ),
    )


class BatterySwapTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "battery_swap_tasks"

    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    station_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("battery_swap_stations.id", ondelete="SET NULL"),
    )

    priority: Mapped[str] = mapped_column(String(16), default=TaskPriority.NORMAL.value, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default=TaskStatus.OPEN.value, nullable=False, index=True,
    )

    assigned_to_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"), index=True,
    )

    battery_level_at_dispatch: Mapped[int | None] = mapped_column(Integer)
    battery_level_after_swap: Mapped[int | None] = mapped_column(Integer)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in TaskStatus)})",
            name="ck_battery_swap_tasks_status",
        ),
    )


class Incident(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    # Can be opened against a ride, scooter, customer or orphan
    ride_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rides.id", ondelete="SET NULL"), index=True,
    )
    scooter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scooters.id", ondelete="SET NULL"), index=True,
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), index=True,
    )

    incident_type: Mapped[str] = mapped_column(String(24), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default=IncidentSeverity.LOW.value, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default=IncidentStatus.OPEN.value, nullable=False, index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    photos: Mapped[list | None] = mapped_column(JSON)

    damage_estimate: Mapped[float | None] = mapped_column(Numeric(12, 2))
    charged_to_customer: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    reported_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
    assigned_to_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            f"incident_type IN ({', '.join(repr(t.value) for t in IncidentType)})",
            name="ck_incidents_type",
        ),
        CheckConstraint(
            f"severity IN ({', '.join(repr(s.value) for s in IncidentSeverity)})",
            name="ck_incidents_severity",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in IncidentStatus)})",
            name="ck_incidents_status",
        ),
    )
