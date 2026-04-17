"""Auth endpoints — OTP, registration, login, refresh, staff login."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.schemas import (
    CustomerLoginIn, CustomerRegisterIn, PhoneOTPRequestIn, PhoneOTPVerifyIn,
    RefreshTokenIn, StaffLoginIn, TokenPair,
)
from app.api.v1.auth.service import AuthService
from app.core.deps import get_db

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


# ─── Customer flows ───────────────────────────────────────────

@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED)
async def request_otp(data: PhoneOTPRequestIn, svc: AuthService = Depends(_service)) -> dict:
    await svc.request_phone_otp(data)
    return {"detail": "OTP sent"}


@router.post("/otp/verify", response_model=TokenPair)
async def verify_otp(data: PhoneOTPVerifyIn, svc: AuthService = Depends(_service)) -> TokenPair:
    return await svc.verify_phone_otp(data)


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(data: CustomerRegisterIn, svc: AuthService = Depends(_service)) -> TokenPair:
    return await svc.register_customer(data)


@router.post("/login", response_model=TokenPair)
async def login(data: CustomerLoginIn, svc: AuthService = Depends(_service)) -> TokenPair:
    return await svc.login_customer(data)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshTokenIn, svc: AuthService = Depends(_service)) -> TokenPair:
    return await svc.refresh_customer(data)


# ─── Staff flows ──────────────────────────────────────────────

@router.post("/staff/login", response_model=TokenPair)
async def staff_login(data: StaffLoginIn, svc: AuthService = Depends(_service)) -> TokenPair:
    return await svc.login_staff(data)
