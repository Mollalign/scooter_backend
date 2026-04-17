"""Customer self-service endpoints (profile + documents)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.customers.schemas import (
    CustomerOut, CustomerUpdateIn, DocumentOut, DocumentUploadIn,
)
from app.api.v1.customers.service import CustomerService
from app.core.deps import get_current_customer, get_db
from app.models.customer import Customer

router = APIRouter()


def _service(db: AsyncSession = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


@router.get("", response_model=CustomerOut)
async def get_me(current: Customer = Depends(get_current_customer)) -> Customer:
    return current


@router.patch("", response_model=CustomerOut)
async def update_me(
    data: CustomerUpdateIn,
    current: Customer = Depends(get_current_customer),
    svc: CustomerService = Depends(_service),
) -> Customer:
    return await svc.update_profile(current, data)


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(
    current: Customer = Depends(get_current_customer),
    svc: CustomerService = Depends(_service),
) -> list:
    return await svc.list_documents(current)


@router.post("/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    data: DocumentUploadIn,
    current: Customer = Depends(get_current_customer),
    svc: CustomerService = Depends(_service),
):
    return await svc.upload_document(current, data)
