from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "ScooterRentalAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/scooter_rental"
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Chapa
    CHAPA_SECRET_KEY: str = ""
    CHAPA_WEBHOOK_SECRET: str = ""
    CHAPA_BASE_URL: str = "https://api.chapa.co/v1"

    # SMS Gateway
    SMS_API_KEY: str = ""
    SMS_API_URL: str = ""
    SMS_SENDER_NAME: str = "ScooterET"

    # Firebase Cloud Messaging
    FCM_SERVER_KEY: str = ""
    FCM_PROJECT_ID: str = ""

    # Cloud Storage (S3-compatible)
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "scooter-rental-uploads"
    S3_REGION: str = "auto"

    # Platform Settings
    PLATFORM_FEE_RATE: float = 0.12
    BOOKING_HOLD_MINUTES: int = 15
    OTP_EXPIRY_MINUTES: int = 10
    MAX_OTP_ATTEMPTS: int = 5

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
