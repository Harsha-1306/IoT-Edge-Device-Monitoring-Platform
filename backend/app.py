import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import init_db
from mqtt_handler import start_mqtt_in_background
from routes.auth import auth_bp
from routes.telemetry import telemetry_bp
from routes.alerts import alerts_bp
from routes.devices import devices_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES

CORS(app, resources={r"/api/*": {"origins": "*"}})
JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(telemetry_bp, url_prefix="/api/telemetry")
app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
app.register_blueprint(devices_bp, url_prefix="/api/devices")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


# Initialize the DB schema (idempotent) and start MQTT listener
init_db()
if os.environ.get("ENABLE_MQTT", "true").lower() == "true":
    start_mqtt_in_background()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
