"""Scooter lookups for the rider — nearby, by QR/code."""

from sqlalchemy.ext.asyncio import AsyncSession


class ScooterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_nearby(
        self, *, lat: float, lng: float, radius_m: int, vehicle_type: str | None,
    ):
        raise NotImplementedError

    async def get_by_code_or_qr(self, identifier: str):
        raise NotImplementedError
