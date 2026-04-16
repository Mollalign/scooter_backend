from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.scooters.router import router as scooters_router
from app.modules.bookings.router import router as bookings_router
from app.modules.payments.router import router as payments_router
from app.modules.wallet.router import router as wallet_router
from app.modules.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: start background job scheduler on startup
    yield
    # TODO: shut down scheduler on shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(scooters_router, prefix="/api/v1/scooters", tags=["Scooters"])
app.include_router(bookings_router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(wallet_router, prefix="/api/v1/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.get("/readiness", tags=["Health"])
async def readiness_check():
    return {"status": "ready", "database": "connected"}
