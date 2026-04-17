"""Ops service — tasks, incidents, remote commands."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.ops.schemas import IncidentIn, IoTCommandIn
from app.models.staff import Staff


class OpsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Tasks ─────────────────────────────────────────────────
    async def my_tasks(self, staff: Staff):
        raise NotImplementedError

    async def claim_task(self, staff: Staff, task_id: UUID):
        raise NotImplementedError

    async def complete_task(self, staff: Staff, task_id: UUID, notes: str | None):
        raise NotImplementedError

    # ── Incidents ─────────────────────────────────────────────
    async def report_incident(self, staff: Staff, data: IncidentIn):
        raise NotImplementedError

    # ── Remote IoT commands ──────────────────────────────────
    async def send_iot_command(
        self, staff: Staff, scooter_id: UUID, data: IoTCommandIn,
    ):
        raise NotImplementedError

    async def force_end_ride(self, staff: Staff, ride_id: UUID, reason: str):
        raise NotImplementedError
