from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookingCreateRequest(BaseModel):
    scooter_id: UUID
    start_time: datetime
    end_time: datetime
    idempotency_key: str | None = Field(None, max_length=100)


class BookingCancelRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)


class BookingResponse(BaseModel):
    id: UUID
    booking_number: str
    customer_id: UUID
    scooter_id: UUID
    owner_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    total_amount: float
    platform_fee: float
    owner_earnings: float
    pickup_confirmed_at: datetime | None
    return_confirmed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingStatusResponse(BaseModel):
    booking_id: UUID
    status: str
    checkout_url: str | None = None


class BookingEventResponse(BaseModel):
    id: UUID
    event_type: str
    from_status: str | None
    to_status: str
    actor_type: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
