import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BookingStatus, PaymentStatus
from app.core.exceptions import AppException, NotFoundException
from app.models.booking import Booking, BookingEvent
from app.models.payment import Payment, PaymentWebhookEvent
from app.modules.bookings.repository import BookingRepository
from app.modules.payments.chapa_client import ChapaClient
from app.modules.payments.repository import PaymentRepository


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)
        self.booking_repo = BookingRepository(db)
        self.chapa = ChapaClient()

    async def initiate_payment(self, booking: Booking, callback_url: str, return_url: str) -> Payment:
        tx_ref = f"SCTR-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment(
            booking_id=booking.id,
            tx_ref=tx_ref,
            provider="chapa",
            amount=float(booking.total_amount),
            currency="ETB",
            status=PaymentStatus.INITIATED,
        )
        payment = await self.repo.create(payment)

        try:
            result = await self.chapa.initialize_transaction(
                amount=float(booking.total_amount),
                tx_ref=tx_ref,
                callback_url=callback_url,
                return_url=return_url,
                customer_name=booking.customer.full_name,
                customer_phone=booking.customer.phone,
            )
            payment.checkout_url = result.get("data", {}).get("checkout_url")
            payment.status = PaymentStatus.PENDING
        except Exception:
            payment.status = PaymentStatus.FAILED

        await self.db.commit()
        return payment

    async def process_webhook(self, tx_ref: str, raw_payload: dict, signature_valid: bool) -> None:
        webhook_event = PaymentWebhookEvent(
            provider="chapa",
            tx_ref=tx_ref,
            signature_valid=signature_valid,
            raw_payload=raw_payload,
            processing_status="received",
        )
        await self.repo.save_webhook_event(webhook_event)

        if not signature_valid:
            webhook_event.processing_status = "failed"
            webhook_event.error_message = "Invalid HMAC signature"
            await self.db.commit()
            return

        payment = await self.repo.get_by_tx_ref(tx_ref)
        if not payment:
            webhook_event.processing_status = "failed"
            webhook_event.error_message = "No payment found for tx_ref"
            await self.db.commit()
            return

        if payment.status == PaymentStatus.SUCCEEDED:
            webhook_event.processing_status = "skipped"
            await self.db.commit()
            return

        await self._verify_and_confirm(payment, webhook_event)

    async def _verify_and_confirm(self, payment: Payment, webhook_event: PaymentWebhookEvent) -> None:
        try:
            result = await self.chapa.verify_transaction(payment.tx_ref)
            chapa_data = result.get("data", {})

            if chapa_data.get("status") == "success" and float(chapa_data.get("amount", 0)) == float(payment.amount):
                payment.status = PaymentStatus.SUCCEEDED
                payment.is_verified = True
                payment.paid_at = datetime.now(timezone.utc)
                payment.provider_transaction_id = chapa_data.get("reference")
                payment.payment_method = chapa_data.get("payment_type")
                payment.webhook_received_at = datetime.now(timezone.utc)

                booking = await self.booking_repo.get_by_id(payment.booking_id)
                if booking and booking.status == BookingStatus.PENDING_PAYMENT:
                    booking.status = BookingStatus.CONFIRMED
                    event = BookingEvent(
                        booking_id=booking.id,
                        event_type="payment_verified",
                        from_status=BookingStatus.PENDING_PAYMENT,
                        to_status=BookingStatus.CONFIRMED,
                        actor_type="system",
                    )
                    self.db.add(event)

                webhook_event.processing_status = "processed"
                webhook_event.processed_at = datetime.now(timezone.utc)
            else:
                payment.status = PaymentStatus.FAILED
                webhook_event.processing_status = "failed"
                webhook_event.error_message = "Chapa verify returned non-success or amount mismatch"
        except Exception as e:
            webhook_event.processing_status = "failed"
            webhook_event.error_message = str(e)

        await self.db.commit()

    async def get_payment_status(self, booking_id: uuid.UUID) -> Payment | None:
        payments = await self.repo.get_by_booking_id(booking_id)
        return payments[0] if payments else None
