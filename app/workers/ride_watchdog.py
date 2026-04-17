"""Detect rides that lost signal or exceeded max duration and force-end them."""

import logging

logger = logging.getLogger(__name__)


async def run_ride_watchdog() -> None:
    logger.debug("Running ride_watchdog tick")
    # TODO: find rides with last_activity_at < now - RIDE_LOST_SIGNAL_MINUTES
    #       and move them to lost_signal / force_ended with safety IoT lock.
