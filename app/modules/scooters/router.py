from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.pagination import PaginationParams
from app.core.permissions import require_owner
from app.models.user import User
from app.modules.scooters.schemas import (
    ScooterCreateRequest,
    ScooterResponse,
    ScooterUpdateRequest,
)
from app.modules.scooters.service import ScooterService

router = APIRouter()


@router.get("", response_model=list[ScooterResponse])
async def search_scooters(
    sub_city: str | None = Query(None),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScooterService(db)
    scooters, total = await service.search_scooters(sub_city, pagination.page, pagination.page_size)
    return scooters


@router.get("/my", response_model=list[ScooterResponse])
async def get_my_scooters(
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = ScooterService(db)
    return await service.get_owner_scooters(owner)


@router.get("/{scooter_id}", response_model=ScooterResponse)
async def get_scooter(
    scooter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScooterService(db)
    return await service.get_scooter(scooter_id)


@router.post("", response_model=ScooterResponse, status_code=201)
async def create_scooter(
    data: ScooterCreateRequest,
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = ScooterService(db)
    return await service.create_scooter(owner, data)


@router.patch("/{scooter_id}", response_model=ScooterResponse)
async def update_scooter(
    scooter_id: UUID,
    data: ScooterUpdateRequest,
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = ScooterService(db)
    return await service.update_scooter(scooter_id, owner, data)
