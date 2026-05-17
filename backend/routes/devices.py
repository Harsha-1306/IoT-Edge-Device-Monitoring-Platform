from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import SessionLocal, Device
from auth import role_required

devices_bp = Blueprint("devices", __name__)


def _serialize(d: Device):
    return {"id": d.id, "device_id": d.device_id, "name": d.name, "location": d.location}


@devices_bp.get("/")
@jwt_required()
def list_devices():
    session = SessionLocal()
    try:
        rows = session.query(Device).order_by(Device.device_id).all()
        return jsonify([_serialize(r) for r in rows])
    finally:
        session.close()


@devices_bp.post("/")
@role_required("admin")
def create_device():
    data = request.get_json() or {}
    if not data.get("device_id") or not data.get("name"):
        return jsonify({"error": "device_id and name required"}), 400
    session = SessionLocal()
    try:
        if session.query(Device).filter_by(device_id=data["device_id"]).first():
            return jsonify({"error": "exists"}), 409
        d = Device(device_id=data["device_id"], name=data["name"], location=data.get("location"))
        session.add(d)
        session.commit()
        return jsonify(_serialize(d)), 201
    finally:
        session.close()
