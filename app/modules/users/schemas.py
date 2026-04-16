from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: UUID
    phone: str
    full_name: str
    fan_number: str
    role: str
    is_phone_verified: bool
    is_document_verified: bool
    city: str
    sub_city: str
    preferred_language: str
    profile_image_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=150)
    sub_city: str | None = Field(None, max_length=100)
    preferred_language: str | None = Field(None, pattern="^(am|en)$")
    profile_image_url: str | None = Field(None, max_length=512)


class DocumentUploadRequest(BaseModel):
    document_type: str = Field(..., pattern="^(national_id_front|national_id_back|scooter_registration|kebele_id)$")
    document_url: str = Field(..., max_length=512)


class DocumentResponse(BaseModel):
    id: UUID
    document_type: str
    document_url: str
    status: str
    review_notes: str | None
    uploaded_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}
