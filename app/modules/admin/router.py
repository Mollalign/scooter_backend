from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.modules.admin.schemas import ApproveScooterRequest, VerifyUserDocumentRequest
from app.modules.admin.service import AdminService

router = APIRouter()


@router.post("/scooters/{scooter_id}/approve")
async def approve_scooter(
    scooter_id: UUID,
    data: ApproveScooterRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    scooter = await service.approve_scooter(scooter_id, admin, data)
    return {"message": "Scooter updated", "status": scooter.status, "is_approved": scooter.is_approved}


@router.post("/documents/{document_id}/verify")
async def verify_document(
    document_id: UUID,
    data: VerifyUserDocumentRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    doc = await service.verify_user_document(document_id, admin, data)
    return {"message": "Document reviewed", "status": doc.status}
