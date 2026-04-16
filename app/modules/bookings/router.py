from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_customer, require_owner
from app.models.user import User
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.schemas import (
    BookingCancelRequest,
    BookingCreateRequest,
    BookingEventResponse,
    BookingResponse,
)
from app.modules.bookings.service import BookingService

router = APIRouter()


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    data: BookingCreateRequest,
    customer: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    booking = await service.create_booking(
        customer=customer,
        scooter_id=data.scooter_id,
        start_time=data.start_time,
        end_time=data.end_time,
        idempotency_key=data.idempotency_key,
    )
    return booking


@router.get("/my", response_model=list[BookingResponse])
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = BookingRepository(db)
    return await repo.get_customer_bookings(current_user.id)


@router.get("/owner", response_model=list[BookingResponse])
async def get_owner_bookings(
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    repo = BookingRepository(db)
    return await repo.get_owner_bookings(owner.id)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    booking = await service.repo.get_by_id(booking_id)
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    data: BookingCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    return await service.cancel_booking(booking_id, current_user, data.reason)


@router.post("/{booking_id}/confirm-pickup", response_model=BookingResponse)
async def confirm_pickup(
    booking_id: UUID,
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    return await service.confirm_pickup(booking_id, owner)


@router.post("/{booking_id}/confirm-return", response_model=BookingResponse)
async def confirm_return(
    booking_id: UUID,
    owner: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    return await service.confirm_return(booking_id, owner)


@router.get("/{booking_id}/events", response_model=list[BookingEventResponse])
async def get_booking_events(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = BookingRepository(db)
    return await repo.get_events(booking_id)
