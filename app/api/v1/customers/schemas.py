"""Customer profile schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    email: EmailStr | None
    full_name: str | None
    fan: str | None
    preferred_language: str
    is_phone_verified: bool
    is_document_verified: bool
    status: str
    total_rides: int
    created_at: datetime


class CustomerUpdateIn(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    preferred_language: str | None = Field(default=None, pattern=r"^(am|en)$")


class DocumentUploadIn(BaseModel):
    document_type: str
    file_url: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: str
    status: str
    file_url: str
    rejection_reason: str | None
    reviewed_at: datetime | None
    created_at: datetime
