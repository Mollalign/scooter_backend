"""Retry failed SMS / push notifications up to N attempts with exponential backoff."""

import logging

logger = logging.getLogger(__name__)


async def run_notification_retry() -> None:
    logger.debug("Running notification_retry tick")
    # TODO: select notifications where status='failed' and attempts < 5
    #       and re-dispatch via SMS / FCM.
