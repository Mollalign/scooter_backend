"""Ride lifecycle schemas — unlock, live status, end, history."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UnlockIn(BaseModel):
    """Unlock by QR scan OR manual code entry."""
    scooter_identifier: str = Field(..., description="QR token or display code like GF-123")
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    reservation_id: UUID | None = None
    idempotency_key: str | None = None


class RidePingIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    speed_kmh: float | None = None
    heading_deg: float | None = None
    battery_percent: int | None = None
    accuracy_m: float | None = None
    recorded_at: datetime


class EndRideIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    idempotency_key: str | None = None


class RideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ride_number: str
    scooter_id: UUID
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int
    distance_km: float
    total_cost: float
    amount_charged: float
    amount_owed: float
    currency: str


class RideSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ride_number: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int
    distance_km: float
    total_cost: float
    status: str
