import json
import logging
import os

import paho.mqtt.client as mqtt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models.gps_data import GPSData
from app.models.vehicle import Vehicle
from app.schemas.gps import GPSUpdate

logger = logging.getLogger(__name__)


def _on_connect(client, userdata, flags, reason_code, properties) -> None:
    if reason_code == 0:
        logger.info("Connected to MQTT broker; subscribing to vehicle GPS topics")
        client.subscribe("vehicles/+/gps", qos=1)
    else:
        logger.error("MQTT connection failed: %s", reason_code)


def _on_message(client, userdata, message) -> None:
    try:
        update = GPSUpdate.model_validate_json(message.payload)
        topic_parts = message.topic.split("/")
        if (
            len(topic_parts) != 3
            or topic_parts[0] != "vehicles"
            or topic_parts[2] != "gps"
            or topic_parts[1] != update.vehicle_id
        ):
            logger.warning("Ignored GPS message with a topic/payload mismatch")
            return

        with SessionLocal() as db:
            vehicle = db.scalar(
                select(Vehicle).where(Vehicle.vehicle_code == update.vehicle_id)
            )
            if vehicle is None:
                logger.warning("Ignored GPS message for unknown vehicle %s", update.vehicle_id)
                return

            db.add(
                GPSData(
                    vehicle_id=vehicle.id,
                    latitude=update.latitude,
                    longitude=update.longitude,
                    speed=update.speed,
                    recorded_at=update.timestamp,
                )
            )
            db.commit()
            logger.info("Saved GPS update for %s", update.vehicle_id)
    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError) as error:
        logger.warning("Ignored invalid GPS message: %s", error)
    except SQLAlchemyError:
        logger.exception("Could not save incoming GPS data")


def start_mqtt_listener() -> mqtt.Client | None:
    if os.getenv("MQTT_ENABLED", "true").lower() not in {"true", "1", "yes"}:
        logger.info("MQTT listener is disabled by MQTT_ENABLED")
        return None

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        # A process-specific ID prevents two local FastAPI runs from repeatedly
        # disconnecting each other from Mosquitto during development.
        client_id=f"vehicle-tracking-fastapi-{os.getpid()}",
    )
    client.on_connect = _on_connect
    client.on_message = _on_message
    broker_host = os.getenv("MQTT_HOST", "127.0.0.1")
    broker_port = int(os.getenv("MQTT_PORT", "1883"))

    # connect_async lets FastAPI start even when the broker is temporarily offline.
    client.connect_async(broker_host, broker_port, keepalive=30)
    client.loop_start()
    return client


def stop_mqtt_listener(client: mqtt.Client | None) -> None:
    if client is not None:
        client.loop_stop()
        client.disconnect()
