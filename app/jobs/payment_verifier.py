import logging

from app.core.database import AsyncSessionLocal
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.chapa_client import ChapaClient

logger = logging.getLogger(__name__)


async def verify_pending_payments():
    async with AsyncSessionLocal() as db:
        try:
            repo = PaymentRepository(db)
            chapa = ChapaClient()
            pending_payments = await repo.get_pending_payments_for_verification()

            for payment in pending_payments:
                try:
                    result = await chapa.verify_transaction(payment.tx_ref)
                    chapa_data = result.get("data", {})

                    if chapa_data.get("status") == "success":
                        logger.info(f"Payment {payment.tx_ref} verified as successful via background job")
                        # TODO: call PaymentService._verify_and_confirm to update payment + booking
                except Exception:
                    logger.warning(f"Failed to verify payment {payment.tx_ref}")

            if pending_payments:
                await db.commit()
        except Exception:
            logger.exception("Error in payment verification job")
            await db.rollback()
