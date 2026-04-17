"""Parking zones + geofences — public read schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Point(BaseModel):
    lat: float
    lng: float


class ParkingZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    center: Point
    is_active: bool
    scooter_count: int = 0


class GeofenceZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    zone_type: str
    speed_limit_kmh: float | None
    priority: int
    polygon_geojson: dict
