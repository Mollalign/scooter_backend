"""Admin panel endpoints (company_admin / super_admin)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin.schemas import (
    CustomerAdminOut, DashboardMetricsOut, PricingPlanIn, PricingPlanOut,
    ScooterAdminIn, ScooterAdminOut,
)
from app.api.v1.admin.service import AdminService
from app.core.deps import get_db
from app.core.permissions import require_admin, require_finance, require_fleet_manager

router = APIRouter(dependencies=[Depends(require_admin)])


def _service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


# ─── Dashboard ─────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardMetricsOut)
async def dashboard(svc: AdminService = Depends(_service)):
    return await svc.dashboard()


# ─── Customers ─────────────────────────────────────────────────

@router.get("/customers", response_model=list[CustomerAdminOut])
async def list_customers(
    q: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: AdminService = Depends(_service),
):
    return await svc.list_customers(q=q, limit=limit, offset=offset)


@router.post("/customers/{customer_id}/suspend", status_code=status.HTTP_204_NO_CONTENT)
async def suspend_customer(
    customer_id: UUID, reason: str, svc: AdminService = Depends(_service),
):
    await svc.suspend_customer(customer_id, reason)


@router.post("/documents/{document_id}/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_document(document_id: UUID, svc: AdminService = Depends(_service)):
    await svc.approve_document(document_id)


@router.post("/documents/{document_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_document(
    document_id: UUID, reason: str, svc: AdminService = Depends(_service),
):
    await svc.reject_document(document_id, reason)


# ─── Scooters ──────────────────────────────────────────────────

@router.post(
    "/scooters",
    response_model=ScooterAdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_fleet_manager)],
)
async def create_scooter(data: ScooterAdminIn, svc: AdminService = Depends(_service)):
    return await svc.create_scooter(data)


@router.get("/scooters", response_model=list[ScooterAdminOut])
async def list_scooters(
    q: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: AdminService = Depends(_service),
):
    return await svc.list_scooters(q=q, status=status_filter, limit=limit, offset=offset)


# ─── Pricing plans ─────────────────────────────────────────────

@router.post(
    "/pricing-plans",
    response_model=PricingPlanOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_pricing_plan(data: PricingPlanIn, svc: AdminService = Depends(_service)):
    return await svc.create_pricing_plan(data)


@router.get("/pricing-plans", response_model=list[PricingPlanOut])
async def list_pricing_plans(svc: AdminService = Depends(_service)):
    return await svc.list_pricing_plans()


# ─── Withdrawals / finance ─────────────────────────────────────

@router.post(
    "/withdrawals/{withdrawal_id}/approve",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_finance)],
)
async def approve_withdrawal(withdrawal_id: UUID, svc: AdminService = Depends(_service)):
    await svc.approve_withdrawal(withdrawal_id)


@router.post(
    "/withdrawals/{withdrawal_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_finance)],
)
async def reject_withdrawal(
    withdrawal_id: UUID, reason: str, svc: AdminService = Depends(_service),
):
    await svc.reject_withdrawal(withdrawal_id, reason)
