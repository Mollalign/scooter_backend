"""Auth business logic: OTP issuance, registration, token management."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.schemas import (
    CustomerLoginIn, CustomerRegisterIn, PhoneOTPRequestIn, PhoneOTPVerifyIn,
    RefreshTokenIn, StaffLoginIn, TokenPair,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Customer ─────────────────────────────────────────────

    async def request_phone_otp(self, data: PhoneOTPRequestIn) -> None:
        raise NotImplementedError

    async def verify_phone_otp(self, data: PhoneOTPVerifyIn) -> TokenPair:
        raise NotImplementedError

    async def register_customer(self, data: CustomerRegisterIn) -> TokenPair:
        raise NotImplementedError

    async def login_customer(self, data: CustomerLoginIn) -> TokenPair:
        raise NotImplementedError

    async def refresh_customer(self, data: RefreshTokenIn) -> TokenPair:
        raise NotImplementedError

    # ─── Staff ────────────────────────────────────────────────

    async def login_staff(self, data: StaffLoginIn) -> TokenPair:
        raise NotImplementedError
