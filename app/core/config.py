""" Scooter Rental Application Configuration Module """

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================

    APP_NAME: str = Field(
        default="Scooter Rental System",
        description="Name of the application"
    )

    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (never True in production!)"
    )

    API_PREFIX: str = Field(
        default="/api",
        description="API prefix for all routes"
    )

    # ==========================================
    # DATABASE SETTINGS
    # ==========================================

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection URL",
        examples=["postgresql+asyncpg://user:password@localhost:5432/scooter_db"]
    )

    DB_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries to console (for debugging)"
    )

    DB_POOL_SIZE: int = Field(
        default=10,
        description="Database connection pool size",
        ge=1,
        le=20
    )

    DB_MAX_OVERFLOW: int = Field(
        default=5,
        description="Maximum overflow connections beyond pool size"
    )

    # ==========================================
    # JWT / AUTHENTICATION SETTINGS
    # ==========================================

    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT signing",
        min_length=32
    )

    ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration time in minutes",
        ge=5,
        le=1440
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=30,
        description="Refresh token expiration time in days",
        ge=1,
        le=30
    )

    ROTATE_REFRESH_TOKENS: bool = Field(
        default=True,
        description="Rotate refresh tokens"
    )

    # ==========================================
    # PAYMENT SETTINGS (CHAPA)
    # ==========================================

    CHAPA_SECRET_KEY: str = Field(
        default="",
        description="Chapa secret key"
    )

    CHAPA_WEBHOOK_SECRET: str = Field(
        default="",
        description="Chapa webhook secret"
    )

    CHAPA_BASE_URL: str = Field(
        default="https://api.chapa.co/v1",
        description="Chapa API base URL"
    )

    # ==========================================
    # SMS GATEWAY SETTINGS
    # ==========================================

    SMS_API_KEY: str = Field(
        default="",
        description="SMS provider API key"
    )

    SMS_API_URL: str = Field(
        default="",
        description="SMS provider API URL"
    )

    SMS_SENDER_NAME: str = Field(
        default="ScooterET",
        description="SMS sender name"
    )

    # ==========================================
    # PUSH NOTIFICATIONS (FCM)
    # ==========================================

    FCM_SERVER_KEY: str = Field(
        default="",
        description="Firebase Cloud Messaging server key"
    )

    FCM_PROJECT_ID: str = Field(
        default="",
        description="Firebase project ID"
    )

    # ==========================================
    # CLOUD STORAGE (S3)
    # ==========================================

    S3_ENDPOINT_URL: str = Field(
        default="",
        description="S3 endpoint URL"
    )

    S3_ACCESS_KEY_ID: str = Field(
        default="",
        description="S3 access key ID"
    )

    S3_SECRET_ACCESS_KEY: str = Field(
        default="",
        description="S3 secret access key"
    )

    S3_BUCKET_NAME: str = Field(
        default="scooter-rental-uploads",
        description="S3 bucket name"
    )

    S3_REGION: str = Field(
        default="auto",
        description="S3 region"
    )

    # ==========================================
    # PLATFORM SETTINGS
    # ==========================================

    PLATFORM_FEE_RATE: float = Field(
        default=0.12,
        description="Platform commission rate (e.g., 0.12 = 12%)",
        ge=0.0,
        le=1.0
    )

    BOOKING_HOLD_MINUTES: int = Field(
        default=15,
        description="Booking hold time before expiration",
        ge=5,
        le=60
    )

    OTP_EXPIRY_MINUTES: int = Field(
        default=10,
        description="OTP expiration time in minutes",
        ge=1,
        le=30
    )

    MAX_OTP_ATTEMPTS: int = Field(
        default=5,
        description="Maximum OTP attempts",
        ge=1,
        le=10
    )

    # ==========================================
    # CORS SETTINGS
    # ==========================================

    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed origins for CORS"
    )

    # ==========================================
    # PYDANTIC CONFIGURATION
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==========================================
    # VALIDATORS
    # ==========================================

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            raise ValueError(
                "DATABASE_URL must start with 'postgresql+asyncpg://'"
            )
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# ==========================================
# SINGLETON PATTERN
# ==========================================

@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()