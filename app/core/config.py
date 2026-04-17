"""Application configuration loaded from environment variables."""

import secrets
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ─── Application ────────────────────────────────────────────
    APP_NAME: str = "GreenFlow Mobility API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # ─── Database ────────────────────────────────────────────────
    DATABASE_URL: str = Field(..., description="postgresql+asyncpg://...")
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=5, ge=0, le=50)
    DB_USE_SSL: bool = False

    # ─── JWT ────────────────────────────────────────────────────
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=5, le=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, ge=1, le=90)
    ROTATE_REFRESH_TOKENS: bool = True

    # ─── Chapa (payments) ───────────────────────────────────────
    CHAPA_SECRET_KEY: str = ""
    CHAPA_PUBLIC_KEY: str = ""
    CHAPA_WEBHOOK_SECRET: str = ""
    CHAPA_BASE_URL: str = "https://api.chapa.co/v1"
    CHAPA_CALLBACK_URL: str = ""   # public URL for Chapa redirect (mobile deep link)
    CHAPA_WEBHOOK_URL: str = ""    # public URL for Chapa webhook

    # ─── SMS ────────────────────────────────────────────────────
    SMS_API_KEY: str = ""
    SMS_API_URL: str = ""
    SMS_SENDER_NAME: str = "GreenFlow"

    # ─── FCM ────────────────────────────────────────────────────
    FCM_SERVER_KEY: str = ""
    FCM_PROJECT_ID: str = ""
    FCM_CREDENTIALS_JSON: str = ""  # path OR raw JSON

    # ─── S3 ─────────────────────────────────────────────────────
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "greenflow-uploads"
    S3_REGION: str = "auto"
    S3_PUBLIC_BASE_URL: str = ""

    # ─── IoT / MQTT ─────────────────────────────────────────────
    MQTT_BROKER_URL: str = ""       # e.g. mqtts://broker.example.com:8883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_CLIENT_ID: str = "greenflow-api"
    MQTT_COMMAND_TOPIC: str = "scooters/{device_id}/cmd"
    MQTT_TELEMETRY_TOPIC: str = "scooters/+/telemetry"
    IOT_COMMAND_TIMEOUT_SECONDS: int = 15

    # ─── Ride / business rules ──────────────────────────────────
    RESERVATION_HOLD_MINUTES: int = Field(default=10, ge=1, le=30)
    RIDE_LOST_SIGNAL_MINUTES: int = Field(default=10, ge=1, le=60)
    RIDE_MAX_DURATION_MINUTES: int = Field(default=180, ge=30, le=720)
    MIN_TOPUP_AMOUNT: float = 10.0
    MAX_TOPUP_AMOUNT: float = 10000.0
    LOW_BATTERY_THRESHOLD: int = Field(default=15, ge=0, le=100)
    MIN_RIDE_BATTERY_PERCENT: int = Field(default=20, ge=0, le=100)

    # ─── OTP ────────────────────────────────────────────────────
    OTP_EXPIRY_MINUTES: int = Field(default=10, ge=1, le=30)
    MAX_OTP_ATTEMPTS: int = Field(default=5, ge=1, le=10)
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # ─── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Validators ─────────────────────────────────────────────

    @field_validator("DATABASE_URL")
    @classmethod
    def _ensure_asyncpg(cls, v: str) -> str:
        if v.startswith("postgresql+asyncpg://"):
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        raise ValueError("DATABASE_URL must use the postgresql+asyncpg driver")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            if v.startswith("["):
                return v
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
