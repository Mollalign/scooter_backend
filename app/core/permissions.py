from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_verified_user
from app.models.user import User


async def require_owner(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    if current_user.role not in ("owner", "both", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )
    return current_user


async def require_customer(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    if current_user.role not in ("customer", "both", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
