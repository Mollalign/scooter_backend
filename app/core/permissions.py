"""
Role-based permission guards for staff endpoints.

Usage:

    @router.post("/scooters", dependencies=[Depends(require_staff_roles(
        StaffRole.FLEET_MANAGER, StaffRole.COMPANY_ADMIN, StaffRole.SUPER_ADMIN
    ))])
"""

from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_staff
from app.core.enums import StaffRole
from app.models.staff import Staff


def require_staff_roles(*roles: StaffRole) -> Callable[..., Staff]:
    allowed = {r.value for r in roles}

    async def _dep(current: Staff = Depends(get_current_staff)) -> Staff:
        if current.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges",
            )
        return current

    return _dep


def _combo(*roles: StaffRole) -> Iterable[StaffRole]:
    return roles


require_super_admin = require_staff_roles(StaffRole.SUPER_ADMIN)
require_admin = require_staff_roles(StaffRole.COMPANY_ADMIN, StaffRole.SUPER_ADMIN)
require_fleet_manager = require_staff_roles(
    StaffRole.FLEET_MANAGER, StaffRole.COMPANY_ADMIN, StaffRole.SUPER_ADMIN
)
require_field_operator = require_staff_roles(
    StaffRole.FIELD_OPERATOR,
    StaffRole.FLEET_MANAGER,
    StaffRole.COMPANY_ADMIN,
    StaffRole.SUPER_ADMIN,
)
require_finance = require_staff_roles(
    StaffRole.FINANCE, StaffRole.COMPANY_ADMIN, StaffRole.SUPER_ADMIN
)
