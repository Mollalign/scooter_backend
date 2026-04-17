"""Mark active reservations that have exceeded their hold window as expired."""

import logging

logger = logging.getLogger(__name__)


async def run_reservation_expiry() -> None:
    logger.debug("Running reservation_expiry tick")
    # TODO: UPDATE reservations SET status='expired' WHERE status='active' AND expires_at < now()
