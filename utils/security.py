import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 310_000
SALT_BYTES = 16
DKLEN = 32


def generate_salt(nbytes: int = SALT_BYTES) -> str:
    return secrets.token_hex(nbytes)


def hash_password(
    password: str,
    salt: str | None = None,
    iterations: int = DEFAULT_ITERATIONS,
) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = salt or generate_salt()
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
        dklen=DKLEN,
    ).hex()

    return f"{ALGORITHM}${iterations}${salt}${derived}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt, expected = encoded_hash.split("$", 3)
        if algorithm != ALGORITHM:
            return False

        iterations = int(iterations_str)
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
            dklen=DKLEN,
        ).hex()

        return hmac.compare_digest(computed, expected)
    except Exception:
        return False