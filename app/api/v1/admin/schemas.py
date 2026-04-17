"""Admin panel schemas — cross-entity admin surface."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DashboardMetricsOut(BaseModel):
    active_rides: int
    scooters_online: int
    scooters_total: int
    low_battery_count: int
    revenue_today: float
    signups_today: int


class CustomerAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    full_name: str | None
    status: str
    is_phone_verified: bool
    is_document_verified: bool
    total_rides: int
    created_at: datetime


class ScooterAdminIn(BaseModel):
    code: str
    qr_code: str
    vehicle_type: str
    model_name: str | None = None
    serial_number: str | None = None
    pricing_plan_id: UUID | None = None


class ScooterAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    qr_code: str
    vehicle_type: str
    status: str
    battery_percent: int | None


class PricingPlanIn(BaseModel):
    name: str
    unlock_fee: float
    per_minute_rate: float
    pause_rate_per_minute: float
    reservation_fee: float = 0
    minimum_charge: float = 0


class PricingPlanOut(PricingPlanIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
