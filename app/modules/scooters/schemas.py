from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScooterCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    model: str = Field(..., max_length=100)
    year: int = Field(..., ge=2000, le=2030)
    license_plate: str = Field(..., max_length=20)
    sub_city: str = Field(..., max_length=100)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    location_description: str | None = Field(None, max_length=255)
    price_per_hour: float = Field(..., ge=0)
    price_per_day: float = Field(..., ge=0)


class ScooterUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    sub_city: str | None = Field(None, max_length=100)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    location_description: str | None = Field(None, max_length=255)
    price_per_hour: float | None = Field(None, ge=0)
    price_per_day: float | None = Field(None, ge=0)
    status: str | None = Field(None, pattern="^(available|maintenance|unlisted)$")


class ScooterSearchParams(BaseModel):
    sub_city: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.5, le=50)
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = None
    sort: str = Field(default="newest", pattern="^(price_asc|price_desc|newest|distance)$")


class ScooterImageResponse(BaseModel):
    id: UUID
    image_url: str
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ScooterResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str | None
    model: str
    year: int
    license_plate: str
    sub_city: str
    location_description: str | None
    price_per_hour: float
    price_per_day: float
    status: str
    is_approved: bool
    images: list[ScooterImageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
