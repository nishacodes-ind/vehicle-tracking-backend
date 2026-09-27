"""Publish changing demo GPS points for BUS-001, BUS-002, or both."""

import argparse
import json
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

ROUTES = {
    "BUS-001": [
        (27.3314, 88.6138),
        (27.3320, 88.6150),
        (27.3330, 88.6162),
        (27.3340, 88.6174),
    ],
    "BUS-002": [
        (27.3200, 88.6000),
        (27.3210, 88.6012),
        (27.3221, 88.6023),
        (27.3230, 88.6035),
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish simulated bus GPS updates over MQTT")
    parser.add_argument("--vehicle", choices=["BUS-001", "BUS-002", "all"], default="all")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between updates")
    parser.add_argument("--host", default=os.getenv("MQTT_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
    args = parser.parse_args()

    vehicles = list(ROUTES) if args.vehicle == "all" else [args.vehicle]
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="vehicle-tracking-gps-simulator",
    )

    try:
        client.connect(args.host, args.port, keepalive=30)
        client.loop_start()
        positions = {vehicle: 0 for vehicle in vehicles}
        speeds = [0, 18, 32, 35]
        print(f"Publishing simulated GPS to MQTT broker {args.host}:{args.port}; press Ctrl+C to stop.")

        while True:
            for vehicle in vehicles:
                points = ROUTES[vehicle]
                index = positions[vehicle] % len(points)
                latitude, longitude = points[index]
                message = {
                    "vehicle_id": vehicle,
                    "latitude": latitude,
                    "longitude": longitude,
                    "speed": speeds[index],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                topic = f"vehicles/{vehicle}/gps"
                result = client.publish(topic, json.dumps(message), qos=1)
                result.wait_for_publish(timeout=3)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"{topic}: {message}")
                else:
                    print(f"Could not publish to {topic}; check the broker connection.")
                positions[vehicle] += 1
            time.sleep(max(args.interval, 0.5))
    except KeyboardInterrupt:
        print("GPS simulator stopped.")
    except OSError as error:
        raise SystemExit(f"Could not connect to MQTT broker: {error}") from error
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
