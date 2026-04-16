from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.admin import AdminAuditLog
from app.models.scooter import Scooter
from app.models.user import User, UserDocument
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import ApproveScooterRequest, VerifyUserDocumentRequest


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminRepository(db)

    async def approve_scooter(self, scooter_id: UUID, admin: User, data: ApproveScooterRequest) -> Scooter:
        result = await self.db.execute(select(Scooter).where(Scooter.id == scooter_id))
        scooter = result.scalar_one_or_none()
        if not scooter:
            raise NotFoundException("Scooter not found")

        before_state = {"is_approved": scooter.is_approved, "status": scooter.status}

        if data.approved:
            scooter.is_approved = True
            scooter.status = "available"
        else:
            scooter.is_approved = False
            scooter.status = "unlisted"

        after_state = {"is_approved": scooter.is_approved, "status": scooter.status}

        log = AdminAuditLog(
            admin_id=admin.id,
            action="approve_scooter" if data.approved else "reject_scooter",
            target_type="scooter",
            target_id=scooter_id,
            before_state=before_state,
            after_state=after_state,
            reason=data.rejection_reason,
        )
        await self.repo.create_audit_log(log)
        await self.db.commit()
        return scooter

    async def verify_user_document(self, document_id: UUID, admin: User, data: VerifyUserDocumentRequest) -> UserDocument:
        result = await self.db.execute(select(UserDocument).where(UserDocument.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundException("Document not found")

        doc.status = "approved" if data.approved else "rejected"
        doc.reviewed_by = admin.id
        doc.review_notes = data.review_notes
        doc.reviewed_at = datetime.now(timezone.utc)

        if data.approved:
            user_result = await self.db.execute(select(User).where(User.id == doc.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.is_document_verified = True

        log = AdminAuditLog(
            admin_id=admin.id,
            action="verify_document" if data.approved else "reject_document",
            target_type="user_document",
            target_id=document_id,
            reason=data.review_notes,
        )
        await self.repo.create_audit_log(log)
        await self.db.commit()
        return doc
