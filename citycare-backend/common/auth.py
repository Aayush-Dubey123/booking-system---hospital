import os
import time
from pathlib import Path

import jwt
from dotenv import load_dotenv
import bcrypt

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

JWT_SECRET = os.environ.get("secret")
JWT_ALGORITHM = os.environ.get("algorithm", "HS256")

def signJWT(role: str, id: str, expiry_duration: int = 3600) -> str:
    payload = {
        "role": role,
        "id": id,
        "expires": time.time() + expiry_duration,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodeJWT(token: str) -> dict | None:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded if decoded.get("expires", 0) > time.time() else None
    except Exception:
        return None


def encrypt_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), 
        hashed_password.encode("utf-8")
    )