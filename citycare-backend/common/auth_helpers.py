from fastapi import HTTPException, status

# pyrefly: ignore [missing-import]
from common.auth import decodeJWT


def verify_token(authorization: str) -> dict:
    """
    Extract and verify JWT from Authorization header.
    Returns the decoded payload dict.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header.",
        )

    token = authorization.split(" ")[1]
    payload = decodeJWT(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    return payload


def require_role(payload: dict, *allowed_roles: str) -> None:
    """
    Raise 403 if the JWT role is not in the allowed list.
    """
    if payload.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
        )
