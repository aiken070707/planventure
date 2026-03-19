import re

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User
from utils.jwt_utils import generate_jwt_token

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.fullmatch(email))


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "invalid email format"}), 400

    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    try:
        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = generate_jwt_token(user.id)
        return (
            jsonify(
                {
                    "message": "user registered",
                    "user": {"id": user.id, "email": user.email},
                    "access_token": token,
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "email already registered"}), 409


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "invalid email format"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    token = generate_jwt_token(user.id)

    return (
        jsonify(
            {
                "message": "login successful",
                "user": {"id": user.id, "email": user.email},
                "access_token": token,
            }
        ),
        200,
    )