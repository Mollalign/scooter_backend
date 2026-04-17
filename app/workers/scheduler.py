"""APScheduler wire-up. Started / stopped from the FastAPI lifespan."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.battery_monitor import run_battery_monitor
from app.workers.chapa_verifier import run_chapa_verifier
from app.workers.notification_retry import run_notification_retry
from app.workers.reservation_expiry import run_reservation_expiry
from app.workers.ride_watchdog import run_ride_watchdog

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler

    _scheduler = AsyncIOScheduler(timezone="UTC")

    _scheduler.add_job(run_reservation_expiry, "interval", seconds=30, id="reservation_expiry")
    _scheduler.add_job(run_ride_watchdog, "interval", seconds=60, id="ride_watchdog")
    _scheduler.add_job(run_chapa_verifier, "interval", seconds=90, id="chapa_verifier")
    _scheduler.add_job(run_notification_retry, "interval", seconds=120, id="notification_retry")
    _scheduler.add_job(run_battery_monitor, "interval", minutes=5, id="battery_monitor")

    _scheduler.start()
    logger.info("Background scheduler started with %d jobs", len(_scheduler.get_jobs()))
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Background scheduler stopped")
