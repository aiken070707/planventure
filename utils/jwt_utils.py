from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from flask import current_app


def generate_jwt_token(
    user_id: int,
    expires_minutes: int | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    expires_minutes = (
        expires_minutes
        if expires_minutes is not None
        else current_app.config.get("JWT_EXPIRES_MINUTES", 60)
    )
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    secret_key = current_app.config["SECRET_KEY"]

    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def validate_jwt_token(token: str) -> dict[str, Any]:
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    secret_key = current_app.config["SECRET_KEY"]

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token.") from exc