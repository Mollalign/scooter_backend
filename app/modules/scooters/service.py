from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.scooter import Scooter
from app.models.user import User
from app.modules.scooters.repository import ScooterRepository
from app.modules.scooters.schemas import ScooterCreateRequest, ScooterUpdateRequest


class ScooterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ScooterRepository(db)

    async def create_scooter(self, owner: User, data: ScooterCreateRequest) -> Scooter:
        scooter = Scooter(
            owner_id=owner.id,
            title=data.title,
            description=data.description,
            model=data.model,
            year=data.year,
            license_plate=data.license_plate,
            sub_city=data.sub_city,
            location_description=data.location_description,
            price_per_hour=data.price_per_hour,
            price_per_day=data.price_per_day,
            status="unlisted",
            is_approved=False,
        )
        # TODO: convert lat/lng to PostGIS geography if provided
        scooter = await self.repo.create(scooter)
        await self.db.commit()
        return scooter

    async def get_scooter(self, scooter_id) -> Scooter:
        scooter = await self.repo.get_by_id(scooter_id)
        if not scooter:
            raise NotFoundException("Scooter not found")
        return scooter

    async def update_scooter(self, scooter_id, owner: User, data: ScooterUpdateRequest) -> Scooter:
        scooter = await self.get_scooter(scooter_id)
        if scooter.owner_id != owner.id:
            raise ForbiddenException("You can only edit your own scooters")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scooter, field, value)

        await self.db.commit()
        await self.db.refresh(scooter)
        return scooter

    async def get_owner_scooters(self, owner: User) -> list[Scooter]:
        return await self.repo.get_by_owner(owner.id)

    async def search_scooters(
        self, sub_city: str | None, page: int, page_size: int
    ) -> tuple[list[Scooter], int]:
        offset = (page - 1) * page_size
        return await self.repo.search(sub_city=sub_city, limit=page_size, offset=offset)
