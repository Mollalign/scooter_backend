from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserDocument


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_documents(self, user_id: UUID) -> list[UserDocument]:
        result = await self.db.execute(
            select(UserDocument).where(UserDocument.user_id == user_id)
        )
        return list(result.scalars().all())

    async def add_document(self, document: UserDocument) -> UserDocument:
        self.db.add(document)
        await self.db.flush()
        return document
