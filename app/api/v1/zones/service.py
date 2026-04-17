"""Zone queries — parking zones + active geofences for the map."""

from sqlalchemy.ext.asyncio import AsyncSession


class ZoneService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_parking_zones(self):
        raise NotImplementedError

    async def list_geofences(self, *, zone_type: str | None = None):
        raise NotImplementedError
