import os

class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://iot:iotpass@localhost:5432/iot_telemetry")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8 hours
    MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
    MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "iot/+/telemetry")
    TEMP_THRESHOLD = float(os.environ.get("TEMP_THRESHOLD", "75"))
    LOAD_THRESHOLD = float(os.environ.get("LOAD_THRESHOLD", "90"))
