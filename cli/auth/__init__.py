"""
cli/auth — JWT/session management package.

Re-exports the public token persistence API so command modules can use:
    from cli.auth import save_token, load_token, clear_token, require_auth, get_role
or:
    from cli import auth as token_store
    token_store.save_token(...)
"""
from cli.auth.token import (
    save_token,
    load_token,
    clear_token,
    get_auth_header,
    require_auth,
    get_role,
)

__all__ = [
    "save_token",
    "load_token",
    "clear_token",
    "get_auth_header",
    "require_auth",
    "get_role",
]
