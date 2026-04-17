"""Create battery-swap tasks for scooters that dropped below the threshold."""

import logging

logger = logging.getLogger(__name__)


async def run_battery_monitor() -> None:
    logger.debug("Running battery_monitor tick")
    # TODO: find scooters below LOW_BATTERY_THRESHOLD without an open swap task,
    #       and create BatterySwapTask entries for dispatch.
