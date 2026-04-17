"""
Seed the database with minimal dev data:
- super admin account
- a few parking zones around Addis Ababa
- a default pricing plan
- a handful of scooters with IoT devices

Run:  python -m scripts.seed
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, create_db_extensions
from app.core.enums import StaffRole
from app.core.security import hash_password
from app.models.pricing import PricingPlan
from app.models.staff import Staff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


async def seed() -> None:
    await create_db_extensions()

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(Staff).where(Staff.email == "admin@greenflow.et")
        )
        if existing:
            logger.info("Super admin already exists, skipping")
        else:
            session.add(
                Staff(
                    email="admin@greenflow.et",
                    full_name="Super Admin",
                    password_hash=hash_password("ChangeMe!123"),
                    role=StaffRole.SUPER_ADMIN.value,
                )
            )
            logger.info("Created super admin: admin@greenflow.et / ChangeMe!123")

        if not await session.scalar(select(PricingPlan).limit(1)):
            session.add(
                PricingPlan(
                    name="Default scooter plan",
                    currency="ETB",
                    unlock_fee=30,
                    per_minute_rate=9,
                    pause_rate_per_minute=3,
                    reservation_fee=5,
                    minimum_charge=10,
                )
            )
            logger.info("Created default pricing plan")

        await session.commit()

    logger.info("Seed complete ✔ (add parking zones + scooters next)")


if __name__ == "__main__":
    asyncio.run(seed())
