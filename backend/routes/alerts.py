from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from models import SessionLocal, Alert
from auth import role_required

alerts_bp = Blueprint("alerts", __name__)


def _serialize(a: Alert):
    return {
        "id": a.id,
        "device_id": a.device_id,
        "metric": a.metric,
        "value": a.value,
        "threshold": a.threshold,
        "severity": a.severity,
        "acknowledged": a.acknowledged,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


@alerts_bp.get("/")
@jwt_required()
def list_alerts():
    limit = min(int(request.args.get("limit", 100)), 500)
    show_ack = request.args.get("acknowledged", "false").lower() == "true"
    session = SessionLocal()
    try:
        q = session.query(Alert)
        if not show_ack:
            q = q.filter(Alert.acknowledged.is_(False))
        rows = q.order_by(desc(Alert.created_at)).limit(limit).all()
        return jsonify([_serialize(r) for r in rows])
    finally:
        session.close()


@alerts_bp.post("/<int:alert_id>/ack")
@role_required("admin", "operator")
def acknowledge(alert_id: int):
    session = SessionLocal()
    try:
        a = session.get(Alert, alert_id)
        if not a:
            return jsonify({"error": "not found"}), 404
        a.acknowledged = True
        session.commit()
        return jsonify(_serialize(a))
    finally:
        session.close()
