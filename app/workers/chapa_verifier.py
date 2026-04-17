"""Poll Chapa for `pending` top-ups older than N seconds (webhook safety-net)."""

import logging

logger = logging.getLogger(__name__)


async def run_chapa_verifier() -> None:
    logger.debug("Running chapa_verifier tick")
    # TODO: for each pending topup, call chapa.verify(tx_ref) and reconcile.
