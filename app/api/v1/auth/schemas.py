"""Auth request/response schemas (customer + staff)."""

from pydantic import BaseModel, EmailStr, Field


# ─── Customer ─────────────────────────────────────────────────

class PhoneOTPRequestIn(BaseModel):
    phone: str = Field(..., description="Ethiopian phone number in any format")


class PhoneOTPVerifyIn(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=8)


class CustomerRegisterIn(BaseModel):
    phone: str
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class CustomerLoginIn(BaseModel):
    phone: str
    password: str


class RefreshTokenIn(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ─── Staff ────────────────────────────────────────────────────

class StaffLoginIn(BaseModel):
    email: EmailStr
    password: str
