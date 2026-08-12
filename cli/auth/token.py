"""
cli/auth/token.py — JWT token persistence for HospitalCare CLI.

Stores token in ~/.hospitalcare/token.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


_TOKEN_DIR = Path.home() / ".hospitalcare"
_TOKEN_FILE = _TOKEN_DIR / "token.json"


def save_token(access_token: str, role: str, hospital_id: Optional[str] = None) -> None:
    """Persist JWT and role to disk."""
    _TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    data = {"access_token": access_token, "role": role, "hospital_id": hospital_id}
    _TOKEN_FILE.write_text(json.dumps(data), encoding="utf-8")


def load_token() -> Optional[dict]:
    """Return stored token dict or None if not logged in."""
    if not _TOKEN_FILE.exists():
        return None
    try:
        return json.loads(_TOKEN_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def clear_token() -> None:
    """Remove stored token (logout)."""
    if _TOKEN_FILE.exists():
        _TOKEN_FILE.unlink()


def get_auth_header() -> Optional[str]:
    """Return 'Bearer <token>' or None if not logged in."""
    token_data = load_token()
    if not token_data:
        return None
    return f"Bearer {token_data['access_token']}"


def require_auth() -> str:
    """Return auth header or raise SystemExit with a friendly message."""
    header = get_auth_header()
    if not header:
        from cli.ui.console import error_exit
        error_exit("You are not logged in. Run [bold]hospitalcare login[/bold] first.")
    return header  # type: ignore[return-value]


def get_role() -> Optional[str]:
    """Return the stored role or None."""
    data = load_token()
    return data.get("role") if data else None
