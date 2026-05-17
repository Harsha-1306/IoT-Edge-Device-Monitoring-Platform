"""MQTT publisher that simulates a fleet of IoT edge devices."""
import json
import math
import os
import random
import time
import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
NUM_DEVICES = int(os.environ.get("DEVICES", "3"))
INTERVAL = float(os.environ.get("INTERVAL_SECONDS", "2"))


def make_payload(device_idx: int, tick: int) -> dict:
    base_temp = 55 + device_idx * 4
    temp = base_temp + 10 * math.sin(tick / 12.0) + random.uniform(-2.5, 2.5)
    load = 60 + 25 * math.sin(tick / 8.0 + device_idx) + random.uniform(-5, 5)
    return {
        "device_id": f"edge-{device_idx + 1:03d}",
        "temperature": round(temp, 2),
        "load_pct": round(max(0.0, min(100.0, load)), 2),
        "position_x": round(50 + 30 * math.sin(tick / 20.0 + device_idx), 2),
        "position_y": round(50 + 30 * math.cos(tick / 20.0 + device_idx), 2),
        "ts": int(time.time()),
    }


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-simulator")
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
            break
        except Exception as e:
            print(f"[sim] waiting for broker: {e}")
            time.sleep(3)
    client.loop_start()
    print(f"[sim] publishing for {NUM_DEVICES} devices every {INTERVAL}s")

    tick = 0
    while True:
        for i in range(NUM_DEVICES):
            payload = make_payload(i, tick)
            topic = f"iot/{payload['device_id']}/telemetry"
            client.publish(topic, json.dumps(payload), qos=1)
        tick += 1
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
