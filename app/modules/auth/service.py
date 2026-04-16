from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, ConflictException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import OTPVerification, User, UserDocument
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import RegisterRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuthRepository(db)

    async def register(self, data: RegisterRequest) -> User:
        existing_phone = await self.repo.get_user_by_phone(data.phone)
        if existing_phone:
            raise ConflictException("Phone number already registered")

        existing_fan = await self.repo.get_user_by_fan_number(data.fan_number)
        if existing_fan:
            raise ConflictException("FAN number already registered")

        user = User(
            phone=data.phone,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            fan_number=data.fan_number,
            role=data.role,
            city=data.city,
            sub_city=data.sub_city,
        )
        user = await self.repo.create_user(user)

        doc = UserDocument(
            user_id=user.id,
            document_type="national_id_front",
            document_url=data.national_id_front_url,
            status="pending",
        )
        self.db.add(doc)

        # TODO: generate OTP, hash it, save to otp_verifications, send via SMS
        await self.db.commit()
        return user

    async def login(self, phone: str, password: str) -> dict:
        user = await self.repo.get_user_by_phone(phone)
        if not user or not verify_password(password, user.password_hash):
            raise AppException("Invalid phone number or password", status_code=401)

        if not user.is_phone_verified:
            raise AppException("Phone number not verified. Please verify OTP first.", status_code=403)

        tokens = self._generate_tokens(user)
        return tokens

    async def verify_otp(self, phone: str, otp: str) -> dict:
        otp_record = await self.repo.get_active_otp(phone, purpose="registration")
        if not otp_record:
            raise AppException("No active OTP found or OTP expired")

        if otp_record.attempts >= settings.MAX_OTP_ATTEMPTS:
            raise AppException("Maximum OTP attempts exceeded. Request a new OTP.")

        if not verify_password(otp, otp_record.otp_hash):
            otp_record.attempts += 1
            await self.db.commit()
            raise AppException("Invalid OTP")

        otp_record.is_used = True

        user = await self.repo.get_user_by_phone(phone)
        if user:
            user.is_phone_verified = True

        await self.db.commit()

        tokens = self._generate_tokens(user)
        return tokens

    def _generate_tokens(self, user: User) -> dict:
        payload = {"sub": str(user.id), "role": user.role}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }
