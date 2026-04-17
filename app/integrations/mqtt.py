"""
MQTT client for IoT command dispatch and telemetry ingestion.

NOTE: The real broker connection is established on app startup (main.py
lifespan). Services publish commands via `publish_command(...)`; the
telemetry subscriber writes to `ride_pings`.
"""

import json
import logging

from app.core.config import settings
from app.core.exceptions import IoTCommandFailedException

logger = logging.getLogger(__name__)

_client = None  # Will hold a connected MQTT client after `connect()` runs


async def connect() -> None:
    global _client
    if not settings.MQTT_BROKER_URL:
        logger.info("MQTT disabled (no broker URL configured)")
        return
    # TODO: use asyncio-mqtt / aiomqtt / paho in production
    logger.info("Connecting MQTT broker: %s", settings.MQTT_BROKER_URL)


async def disconnect() -> None:
    global _client
    if _client is None:
        return
    logger.info("Disconnecting MQTT broker")
    _client = None


async def publish_command(*, device_id: str, payload: dict) -> None:
    topic = settings.MQTT_COMMAND_TOPIC.format(device_id=device_id)
    body = json.dumps(payload)
    if _client is None:
        logger.info("[MQTT disabled] publish %s -> %s", topic, body)
        return
    try:
        # TODO: await _client.publish(topic, body, qos=1)
        raise NotImplementedError
    except Exception as exc:
        logger.exception("MQTT publish failed")
        raise IoTCommandFailedException() from exc
