"""
auth_cmd.py — Authentication commands: login, signup, logout, whoami.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone

import typer

import cli.auth as token_store
from cli.services import api_client as client
import cli.ui as ui

auth_app = typer.Typer(
    name="auth",
    help="Authentication commands (login, signup, logout, whoami).",
    no_args_is_help=True,
)


@auth_app.command("signup")
def signup():
    """
    Create a new patient account.
    """
    ui.print_banner()
    ui.console.print("[bold]Create a new patient account[/bold]\n")

    first_name = ui.prompt("First name")
    last_name = ui.prompt("Last name")
    email = ui.prompt("Email")
    password = ui.prompt("Password (min 8 chars)", password=True)

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
    }

    with ui.spinner("Creating account..."):
        result = client.post("/v1/users/signup", payload)

    ui.success(
        f"Account created! Welcome, "
        f"[bold]{result.get('first_name')} {result.get('last_name')}[/bold]. "
        "Run [bold cyan]hospitalcare login[/bold cyan] to get started."
    )


@auth_app.command("login")
def login():
    """
    Log in with your email and password. Saves JWT locally.
    """
    ui.print_banner()
    ui.console.print("[bold]Sign in to CityCare[/bold]\n")

    email = ui.prompt("Email")
    password = ui.prompt("Password", password=True)

    payload = {
        "email": email,
        "password": password,
    }

    with ui.spinner("Authenticating..."):
        result = client.post("/v1/users/login", payload)

    token_store.save_token(
        access_token=result["access_token"],
        role=result["role"],
        hospital_id=result.get("hospital_id"),
    )

    role_badge = f"[bold magenta]{result['role']}[/bold magenta]"
    ui.success(f"Logged in as {role_badge}. Token saved.")


@auth_app.command("logout")
def logout():
    """
    Log out and remove the stored JWT from disk.
    """
    if not token_store.load_token():
        ui.warning("You are not currently logged in.")
        return

    token_store.clear_token()
    ui.success("Logged out. Token removed.")


@auth_app.command("whoami")
def whoami():
    """
    Show currently authenticated user information from the stored JWT.
    """
    data = token_store.load_token()

    if not data:
        ui.error_exit(
            "Not logged in. Run [bold]hospitalcare login[/bold]."
        )

    token = data.get("access_token")

    if not token:
        ui.error_exit("Stored authentication token is invalid. Please login again.")

    # Decode JWT payload for display only.
    # Signature verification is intentionally NOT performed here because
    # this command only displays information. The backend remains responsible
    # for authenticating protected API requests.
    try:
        parts = token.split(".")

        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        payload_part = parts[1]

        # JWT Base64URL padding
        padded = payload_part + "=" * (-len(payload_part) % 4)

        payload = json.loads(
            base64.urlsafe_b64decode(padded).decode("utf-8")
        )

    except Exception:
        ui.error_exit(
            "Could not decode the stored token. Please login again."
        )

    body = (
        f"[bold]Role:[/bold]        {data.get('role', 'N/A')}\n"
        f"[bold]User ID:[/bold]     {payload.get('id', 'N/A')}\n"
        f"[bold]Hospital ID:[/bold] {data.get('hospital_id') or '—'}\n"
        f"[bold]Expires:[/bold]     {_format_exp(payload.get('exp'))}"
    )

    from rich.panel import Panel

    ui.console.print(
        Panel(
            body,
            title="Who Am I",
            border_style="cyan",
        )
    )


def _format_exp(exp) -> str:
    """
    Convert JWT expiration timestamp into readable UTC time.
    """
    if exp is None:
        return "N/A"

    try:
        dt = datetime.fromtimestamp(
            int(exp),
            tz=timezone.utc,
        )
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(exp)