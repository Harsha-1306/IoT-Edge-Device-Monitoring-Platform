from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import SessionLocal, User
from auth import verify_password, hash_password, role_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid credentials"}), 401
        token = create_access_token(
            identity=user.username,
            additional_claims={"role": user.role, "uid": user.id},
        )
        return jsonify({
            "access_token": token,
            "user": {"username": user.username, "role": user.role}
        })
    finally:
        session.close()


@auth_bp.post("/register")
@role_required("admin")
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = data.get("role", "viewer")
    if role not in ("admin", "operator", "viewer"):
        return jsonify({"error": "invalid role"}), 400
    if not username or len(password) < 6:
        return jsonify({"error": "username and password (>=6 chars) required"}), 400

    session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "user exists"}), 409
        u = User(username=username, password_hash=hash_password(password), role=role)
        session.add(u)
        session.commit()
        return jsonify({"id": u.id, "username": u.username, "role": u.role}), 201
    finally:
        session.close()


@auth_bp.get("/me")
@jwt_required()
def me():
    claims = get_jwt()
    return jsonify({"username": get_jwt_identity(), "role": claims.get("role")})
