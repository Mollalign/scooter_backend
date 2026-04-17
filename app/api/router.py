"""Aggregates every v1 feature router under a single object."""

from fastapi import APIRouter

from app.api.v1.admin.router import router as admin_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.customers.router import router as customers_router
from app.api.v1.ops.router import router as ops_router
from app.api.v1.reservations.router import router as reservations_router
from app.api.v1.rides.router import router as rides_router
from app.api.v1.scooters.router import router as scooters_router
from app.api.v1.wallet.router import router as wallet_router
from app.api.v1.webhooks.router import router as webhooks_router
from app.api.v1.zones.router import router as zones_router

api_router = APIRouter()

# ─── Customer-facing (mobile app) ─────────────────────────────
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(customers_router, prefix="/me", tags=["Customer"])
api_router.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
api_router.include_router(zones_router, prefix="/zones", tags=["Zones"])
api_router.include_router(scooters_router, prefix="/scooters", tags=["Scooters"])
api_router.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])
api_router.include_router(rides_router, prefix="/rides", tags=["Rides"])

# ─── Webhooks (public, signed) ────────────────────────────────
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

# ─── Internal (staff) ─────────────────────────────────────────
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(ops_router, prefix="/ops", tags=["Operations"])
