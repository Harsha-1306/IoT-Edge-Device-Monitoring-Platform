from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from models import SessionLocal, Telemetry
from auth import role_required

telemetry_bp = Blueprint("telemetry", __name__)


def _serialize(t: Telemetry):
    return {
        "id": t.id,
        "device_id": t.device_id,
        "temperature": t.temperature,
        "load_pct": t.load_pct,
        "position_x": t.position_x,
        "position_y": t.position_y,
        "recorded_at": t.recorded_at.isoformat() if t.recorded_at else None,
    }


@telemetry_bp.get("/")
@jwt_required()
def list_telemetry():
    limit = min(int(request.args.get("limit", 100)), 1000)
    device_id = request.args.get("device_id")
    session = SessionLocal()
    try:
        q = session.query(Telemetry)
        if device_id:
            q = q.filter(Telemetry.device_id == device_id)
        rows = q.order_by(desc(Telemetry.recorded_at)).limit(limit).all()
        return jsonify([_serialize(r) for r in rows])
    finally:
        session.close()


@telemetry_bp.get("/latest")
@jwt_required()
def latest_per_device():
    """Return the most recent telemetry per device for dashboard tiles."""
    session = SessionLocal()
    try:
        sql = """
            SELECT DISTINCT ON (device_id) id, device_id, temperature, load_pct,
                position_x, position_y, recorded_at
            FROM telemetry
            ORDER BY device_id, recorded_at DESC
        """
        rows = session.execute(__import__("sqlalchemy").text(sql)).mappings().all()
        return jsonify([dict(r) | {"recorded_at": r["recorded_at"].isoformat()} for r in rows])
    finally:
        session.close()


@telemetry_bp.post("/")
@role_required("admin", "operator")
def ingest_telemetry():
    """REST ingestion path (in addition to MQTT) for testing or HTTP-only devices."""
    data = request.get_json() or {}
    if not data.get("device_id"):
        return jsonify({"error": "device_id required"}), 400
    session = SessionLocal()
    try:
        t = Telemetry(
            device_id=data["device_id"],
            temperature=data.get("temperature"),
            load_pct=data.get("load_pct"),
            position_x=data.get("position_x"),
            position_y=data.get("position_y"),
        )
        session.add(t)
        session.commit()
        return jsonify(_serialize(t)), 201
    finally:
        session.close()
