from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20, examples=["+251911234567"])
    full_name: str = Field(..., min_length=2, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)
    fan_number: str = Field(..., min_length=4, max_length=20)
    city: str = Field(default="Addis Ababa", max_length=100)
    sub_city: str = Field(..., max_length=100, examples=["Bole"])
    role: str = Field(default="customer", pattern="^(customer|owner|both)$")
    national_id_front_url: str = Field(..., max_length=512)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)


class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
