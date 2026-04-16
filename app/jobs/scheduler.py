from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.jobs.booking_expiry import expire_pending_bookings
from app.jobs.payment_verifier import verify_pending_payments
from app.jobs.notification_retry import retry_failed_notifications

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(expire_pending_bookings, "interval", minutes=1, id="booking_expiry")
    scheduler.add_job(verify_pending_payments, "interval", minutes=5, id="payment_verifier")
    scheduler.add_job(retry_failed_notifications, "interval", minutes=3, id="notification_retry")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)
