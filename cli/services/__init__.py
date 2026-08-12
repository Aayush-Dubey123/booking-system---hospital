"""
cli/services — API and backend interaction package.

Re-exports the full HTTP client API from api_client.py so command modules can use:
    from cli.services import get, post, put, stream_post
or:
    from cli import client
    client.get(...)
"""
from cli.services.api_client import (
    BASE_URL,
    TIMEOUT,
    get,
    post,
    put,
    stream_post,
)

__all__ = [
    "BASE_URL",
    "TIMEOUT",
    "get",
    "post",
    "put",
    "stream_post",
]
