from functools import wraps

from flask import g, jsonify, request

from models import User
from utils.jwt_utils import validate_jwt_token


def jwt_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "").strip()
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "missing or invalid Authorization header"}), 401

        token = parts[1]

        try:
            payload = validate_jwt_token(token)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 401

        user_id = payload.get("sub")
        if not user_id:
            return jsonify({"error": "invalid token payload"}), 401

        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify({"error": "user not found"}), 401

        g.current_user = user
        g.jwt_payload = payload

        return view_func(*args, **kwargs)

    return wrapped