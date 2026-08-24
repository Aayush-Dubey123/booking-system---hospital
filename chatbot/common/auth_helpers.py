import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
from fastapi import HTTPException, status
from jose import JWTError, jwt

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

SECRET_KEY = os.environ.get("secret", "your-secret-key")
ALGORITHM = os.environ.get("algorithm", "HS256")


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


def require_role(payload: dict, required_role: str):
    """Check if user has required role."""
    user_role = payload.get("role")
    if user_role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This operation requires {required_role} role",
        )


def create_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
