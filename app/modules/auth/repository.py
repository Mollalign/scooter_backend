from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import OTPVerification, User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_user_by_fan_number(self, fan_number: str) -> User | None:
        result = await self.db.execute(select(User).where(User.fan_number == fan_number))
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_otp(self, otp: OTPVerification) -> OTPVerification:
        self.db.add(otp)
        await self.db.flush()
        return otp

    async def get_active_otp(self, phone: str, purpose: str) -> OTPVerification | None:
        result = await self.db.execute(
            select(OTPVerification)
            .where(
                OTPVerification.phone == phone,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used == False,  # noqa: E712
                OTPVerification.expires_at > datetime.now(timezone.utc),
            )
            .order_by(OTPVerification.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
