"""Reservation schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReservationIn(BaseModel):
    scooter_id: UUID


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scooter_id: UUID
    status: str
    expires_at: datetime
    fee_charged: float
    created_at: datetime
