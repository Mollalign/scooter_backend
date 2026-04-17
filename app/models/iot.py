"""IoT hardware: device registry + command audit log."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import IoTCommandStatus, IoTCommandTrigger, IoTCommandType
from app.models.base import Base, TimestampMixin, UUIDMixin


class IoTDevice(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "iot_devices"

    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )

    imei: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    iccid: Mapped[str | None] = mapped_column(String(32), unique=True)
    msisdn: Mapped[str | None] = mapped_column(String(20))

    firmware_version: Mapped[str | None] = mapped_column(String(32))
    hardware_version: Mapped[str | None] = mapped_column(String(32))
    vendor: Mapped[str | None] = mapped_column(String(64))

    mqtt_topic: Mapped[str | None] = mapped_column(String(200))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    signal_strength: Mapped[int | None] = mapped_column(Integer)

    scooter = relationship("Scooter", back_populates="iot_device")


class IoTCommand(UUIDMixin, TimestampMixin, Base):
    """Append-only audit trail of every command sent to a device."""

    __tablename__ = "iot_commands"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("iot_devices.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    scooter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scooters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    command: Mapped[str] = mapped_column(String(24), nullable=False)
    trigger: Mapped[str] = mapped_column(String(24), nullable=False)

    ride_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rides.id", ondelete="SET NULL"), index=True,
    )
    issued_by_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff.id", ondelete="SET NULL"),
    )

    payload: Mapped[dict | None] = mapped_column(JSON)
    response: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(
        String(16), default=IoTCommandStatus.SENT.value, nullable=False, index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f"command IN ({', '.join(repr(c.value) for c in IoTCommandType)})",
            name="ck_iot_commands_command",
        ),
        CheckConstraint(
            f"trigger IN ({', '.join(repr(t.value) for t in IoTCommandTrigger)})",
            name="ck_iot_commands_trigger",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s.value) for s in IoTCommandStatus)})",
            name="ck_iot_commands_status",
        ),
    )
