"""Field operator / fleet manager endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.ops.schemas import IncidentIn, IoTCommandIn, TaskOut
from app.api.v1.ops.service import OpsService
from app.core.deps import get_current_staff, get_db
from app.core.permissions import require_field_operator, require_fleet_manager
from app.models.staff import Staff

router = APIRouter(dependencies=[Depends(require_field_operator)])


def _service(db: AsyncSession = Depends(get_db)) -> OpsService:
    return OpsService(db)


# ─── Task management ──────────────────────────────────────────

@router.get("/tasks", response_model=list[TaskOut])
async def my_tasks(
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    return await svc.my_tasks(staff)


@router.post("/tasks/{task_id}/claim", status_code=status.HTTP_204_NO_CONTENT)
async def claim_task(
    task_id: UUID,
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    await svc.claim_task(staff, task_id)


@router.post("/tasks/{task_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_task(
    task_id: UUID,
    notes: str | None = None,
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    await svc.complete_task(staff, task_id, notes)


# ─── Incidents ────────────────────────────────────────────────

@router.post("/incidents", status_code=status.HTTP_201_CREATED)
async def report_incident(
    data: IncidentIn,
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    return await svc.report_incident(staff, data)


# ─── IoT commands (fleet manager+) ────────────────────────────

@router.post(
    "/scooters/{scooter_id}/command",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_fleet_manager)],
)
async def send_command(
    scooter_id: UUID,
    data: IoTCommandIn,
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    return await svc.send_iot_command(staff, scooter_id, data)


@router.post(
    "/rides/{ride_id}/force-end",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_fleet_manager)],
)
async def force_end_ride(
    ride_id: UUID,
    reason: str,
    staff: Staff = Depends(get_current_staff),
    svc: OpsService = Depends(_service),
):
    return await svc.force_end_ride(staff, ride_id, reason)
