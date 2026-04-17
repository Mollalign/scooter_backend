"""Customer-facing scooter schemas (map + detail + nearby search)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScooterMapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    vehicle_type: str
    battery_percent: int | None
    range_km: float | None
    lat: float
    lng: float
    parking_zone_id: UUID | None


class ScooterDetailOut(ScooterMapOut):
    model_name: str | None
    status: str
    price_per_minute: float | None
    unlock_fee: float | None


class NearbyQuery(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_m: int = Field(1500, ge=50, le=10_000)
    vehicle_type: str | None = None
