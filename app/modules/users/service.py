from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserDocument
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import DocumentUploadRequest, ProfileUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_profile(self, user: User) -> User:
        return user

    async def update_profile(self, user: User, data: ProfileUpdateRequest) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def upload_document(self, user: User, data: DocumentUploadRequest) -> UserDocument:
        doc = UserDocument(
            user_id=user.id,
            document_type=data.document_type,
            document_url=data.document_url,
            status="pending",
        )
        doc = await self.repo.add_document(doc)
        await self.db.commit()
        return doc

    async def get_documents(self, user: User) -> list[UserDocument]:
        return await self.repo.get_documents(user.id)
