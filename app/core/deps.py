"""
FastAPI dependency functions.

- `get_db`            → async SQLAlchemy session
- `get_current_customer` / `get_current_verified_customer`
- `get_current_staff`
"""

from uuid import UUID
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.enums import CustomerStatus, StaffStatus
from app.core.security import decode_token
from app.models.customer import Customer
from app.models.staff import Staff

_bearer = HTTPBearer(auto_error=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def _unauthorized(detail: str = "Invalid or expired token") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _decode_subject(
    credentials: HTTPAuthorizationCredentials, expected_audience: str
) -> UUID:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise _unauthorized()
    if payload.get("aud") != expected_audience:
        raise _unauthorized("Token not valid for this endpoint")
    sub = payload.get("sub")
    if not sub:
        raise _unauthorized("Malformed token payload")
    try:
        return UUID(sub)
    except ValueError as exc:
        raise _unauthorized("Malformed token subject") from exc


# ──────────────────────────────────────────────────────────────
# Customer auth
# ──────────────────────────────────────────────────────────────

async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> Customer:
    customer_id = await _decode_subject(credentials, expected_audience="customer")
    customer = await db.scalar(select(Customer).where(Customer.id == customer_id))
    if customer is None:
        raise _unauthorized("Customer not found")
    if customer.status == CustomerStatus.DEACTIVATED:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account deactivated")
    if customer.status == CustomerStatus.SUSPENDED:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account suspended")
    return customer


async def get_current_verified_customer(
    current: Customer = Depends(get_current_customer),
) -> Customer:
    if not current.is_phone_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Phone not verified")
    if not current.is_document_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Identity verification pending. You will be notified when approved.",
        )
    if current.status == CustomerStatus.BLOCKED_UNPAID:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            "Outstanding balance. Top up your wallet to continue riding.",
        )
    return current


# ──────────────────────────────────────────────────────────────
# Staff auth
# ──────────────────────────────────────────────────────────────

async def get_current_staff(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> Staff:
    staff_id = await _decode_subject(credentials, expected_audience="staff")
    staff = await db.scalar(select(Staff).where(Staff.id == staff_id))
    if staff is None:
        raise _unauthorized("Staff user not found")
    if staff.status != StaffStatus.ACTIVE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff account inactive")
    return staff
