"""Field operator / fleet manager schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scooter_id: UUID
    task_type: str
    priority: str
    status: str
    title: str
    description: str | None
    created_at: datetime


class IncidentIn(BaseModel):
    scooter_id: UUID | None = None
    ride_id: UUID | None = None
    customer_id: UUID | None = None
    incident_type: str
    severity: str = "medium"
    title: str
    description: str | None = None
    photos: list[str] | None = None


class IoTCommandIn(BaseModel):
    command: str
    reason: str | None = None
