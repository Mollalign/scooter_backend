from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scooter import Scooter, ScooterImage


class ScooterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, scooter: Scooter) -> Scooter:
        self.db.add(scooter)
        await self.db.flush()
        return scooter

    async def get_by_id(self, scooter_id: UUID) -> Scooter | None:
        result = await self.db.execute(select(Scooter).where(Scooter.id == scooter_id))
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> list[Scooter]:
        result = await self.db.execute(
            select(Scooter).where(Scooter.owner_id == owner_id).order_by(Scooter.created_at.desc())
        )
        return list(result.scalars().all())

    async def search(
        self,
        sub_city: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Scooter], int]:
        query = select(Scooter).where(
            Scooter.status == "available",
            Scooter.is_approved == True,  # noqa: E712
        )

        if sub_city:
            query = query.where(Scooter.sub_city == sub_city)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(Scooter.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        scooters = list(result.scalars().all())

        return scooters, total

    async def add_image(self, image: ScooterImage) -> ScooterImage:
        self.db.add(image)
        await self.db.flush()
        return image
