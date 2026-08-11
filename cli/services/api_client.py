"""
cli/services/api_client.py — httpx API client for HospitalCare CLI.

All API calls go through this module. Auth header is injected automatically.
"""
from __future__ import annotations

import json
import sys
from typing import Optional

import httpx


BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


def _handle_response(response: httpx.Response) -> dict | list:
    """
    Parse API response and raise clean exceptions for API errors.
    The CLI command layer is responsible for displaying the error.
    """

    if response.status_code == 401:
        raise RuntimeError(
            "Session expired or unauthorized. "
            "Run hospitalcare login to re-authenticate."
        )

    if response.status_code == 403:
        raise RuntimeError(
            "Access denied. You do not have permission to perform this action."
        )

    if response.status_code == 404:
        try:
            detail = response.json().get(
                "detail",
                "Resource not found.",
            )
        except Exception:
            detail = "Resource not found."

        raise RuntimeError(str(detail))

    if response.status_code >= 400:
        try:
            detail = response.json().get(
                "detail",
                response.text,
            )
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Error {response.status_code}: {detail}"
        )

    try:
        return response.json()
    except Exception:
        return {}


def get(
    endpoint: str,
    auth: Optional[str] = None,
    params: Optional[dict] = None,
) -> dict | list:
    """
    Perform a GET request.
    """

    headers = {}

    if auth:
        headers["Authorization"] = auth

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
        ) as client:

            response = client.get(
                endpoint,
                headers=headers,
                params=params,
            )

            return _handle_response(response)

    except httpx.ConnectError:
        _connection_error()

    except httpx.TimeoutException:
        _timeout_error()


def post(
    endpoint: str,
    data: dict,
    auth: Optional[str] = None,
) -> dict | list:
    """
    Perform a POST request.
    """

    headers = {
        "Content-Type": "application/json"
    }

    if auth:
        headers["Authorization"] = auth

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
        ) as client:

            response = client.post(
                endpoint,
                json=data,
                headers=headers,
            )

            return _handle_response(response)

    except httpx.ConnectError:
        _connection_error()

    except httpx.TimeoutException:
        _timeout_error()


def put(
    endpoint: str,
    auth: Optional[str] = None,
    data: Optional[dict] = None,
) -> dict | list:
    """
    Perform a PUT request.
    """

    headers = {
        "Content-Type": "application/json"
    }

    if auth:
        headers["Authorization"] = auth

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
        ) as client:

            response = client.put(
                endpoint,
                json=data or {},
                headers=headers,
            )

            return _handle_response(response)

    except httpx.ConnectError:
        _connection_error()

    except httpx.TimeoutException:
        _timeout_error()


def stream_post(
    endpoint: str,
    data: dict,
    auth: Optional[str] = None,
) -> None:
    """
    Stream SSE events from /v1/chat/stream.
    """

    from cli.ui import console

    headers = {
        "Content-Type": "application/json"
    }

    if auth:
        headers["Authorization"] = auth

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=60.0,
        ) as client:

            with client.stream(
                "POST",
                endpoint,
                json=data,
                headers=headers,
            ) as response:

                if response.status_code == 401:
                    console.print(
                        "\n[bold red]Session expired.[/bold red] "
                        "Run [cyan]hospitalcare login[/cyan]."
                    )
                    sys.exit(1)

                if response.status_code == 403:
                    console.print(
                        "\n[bold red]Access denied.[/bold red]"
                    )
                    sys.exit(1)

                if response.status_code == 404:
                    try:
                        detail = response.json().get(
                            "detail",
                            "Resource not found.",
                        )
                    except Exception:
                        detail = "Resource not found."

                    console.print(
                        f"\n[yellow]Not found:[/yellow] {detail}"
                    )
                    sys.exit(1)

                if response.status_code >= 400:
                    console.print(
                        f"\n[bold red]Error "
                        f"{response.status_code}[/bold red]"
                    )
                    sys.exit(1)

                for line in response.iter_lines():

                    if not line:
                        continue

                    if not line.startswith("data:"):
                        continue

                    raw = line[5:].strip()

                    try:
                        payload = json.loads(raw)
                    except Exception:
                        continue

                    if "text" in payload:
                        print(
                            payload["text"],
                            end="",
                            flush=True,
                        )

                    elif "response" in payload:
                        print()
                        break

                    elif "message" in payload:
                        console.print(
                            f"\n[red]Error: "
                            f"{payload['message']}[/red]"
                        )
                        break

    except httpx.ConnectError:
        _connection_error()

    except httpx.TimeoutException:
        _timeout_error()


def _connection_error() -> None:
    """
    Handle backend connection failure cleanly.
    """

    from cli.ui import console

    console.print(
        "\n[bold red]Cannot connect to the CityCare backend.[/bold red]\n"
        "   Make sure the server is running at "
        "[cyan]http://localhost:8000[/cyan]"
    )

    sys.exit(1)


def _timeout_error() -> None:
    """
    Handle backend timeout cleanly.
    """

    from cli.ui import console

    console.print(
        "\n[bold red]Request timed out.[/bold red] "
        "The server took too long to respond."
    )

    sys.exit(1)
