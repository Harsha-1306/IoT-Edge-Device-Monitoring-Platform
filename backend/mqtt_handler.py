import json
import threading
import logging
import paho.mqtt.client as mqtt
from models import SessionLocal, Telemetry, Alert
from config import Config

log = logging.getLogger("mqtt")


def _on_connect(client, userdata, flags, reason_code, properties=None):
    log.info("MQTT connected rc=%s, subscribing to %s", reason_code, Config.MQTT_TOPIC)
    client.subscribe(Config.MQTT_TOPIC, qos=1)


def _check_thresholds(session, device_id, temperature, load_pct):
    if temperature is not None and temperature > Config.TEMP_THRESHOLD:
        session.add(Alert(
            device_id=device_id, metric="temperature",
            value=temperature, threshold=Config.TEMP_THRESHOLD,
            severity="critical" if temperature > Config.TEMP_THRESHOLD * 1.1 else "warning",
        ))
    if load_pct is not None and load_pct > Config.LOAD_THRESHOLD:
        session.add(Alert(
            device_id=device_id, metric="load_pct",
            value=load_pct, threshold=Config.LOAD_THRESHOLD,
            severity="critical" if load_pct > 95 else "warning",
        ))


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Topic format: iot/<device_id>/telemetry
        parts = msg.topic.split("/")
        device_id = parts[1] if len(parts) >= 2 else payload.get("device_id", "unknown")
        session = SessionLocal()
        try:
            t = Telemetry(
                device_id=device_id,
                temperature=payload.get("temperature"),
                load_pct=payload.get("load_pct"),
                position_x=payload.get("position_x"),
                position_y=payload.get("position_y"),
            )
            session.add(t)
            _check_thresholds(session, device_id, t.temperature, t.load_pct)
            session.commit()
        except Exception as e:
            session.rollback()
            log.exception("DB write failed: %s", e)
        finally:
            session.close()
    except Exception as e:
        log.exception("Failed to handle MQTT message: %s", e)


def start_mqtt_in_background():
    def _run():
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-backend-sub")
        client.on_connect = _on_connect
        client.on_message = _on_message
        while True:
            try:
                client.connect(Config.MQTT_HOST, Config.MQTT_PORT, keepalive=30)
                client.loop_forever()
            except Exception as e:
                log.warning("MQTT loop crashed, retrying: %s", e)
                import time
                time.sleep(3)

    t = threading.Thread(target=_run, daemon=True, name="mqtt-subscriber")
    t.start()
    return t
