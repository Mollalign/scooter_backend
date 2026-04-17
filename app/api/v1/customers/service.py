"""Customer profile service (self-service for the rider)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.customers.schemas import CustomerUpdateIn, DocumentUploadIn
from app.models.customer import Customer, CustomerDocument


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_profile(self, customer: Customer, data: CustomerUpdateIn) -> Customer:
        raise NotImplementedError

    async def list_documents(self, customer: Customer) -> list[CustomerDocument]:
        raise NotImplementedError

    async def upload_document(
        self, customer: Customer, data: DocumentUploadIn
    ) -> CustomerDocument:
        raise NotImplementedError
