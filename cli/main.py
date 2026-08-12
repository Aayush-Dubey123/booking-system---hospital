"""
main.py — HospitalCare CLI entry point.

Assembles all command groups into the root `hospitalcare` Typer app.
"""
from __future__ import annotations

# pyrefly: ignore [missing-import]
import typer

from cli.commands.auth_cmd import auth_app
from cli.commands.hospital_cmd import hospitals_app
from cli.commands.slots_cmd import slots_app
from cli.commands.book_cmd import book_app
from cli.commands.appointments_cmd import appointments_app
from cli.commands.prescriptions_cmd import prescriptions_app
from cli.commands.chat_cmd import chat_app
import cli.ui as ui

app = typer.Typer(
    name="hospitalcare",
    help=(
        "🏥  HospitalCare CLI — terminal frontend for CityCare Clinic.\n\n"
        "Run [bold cyan]hospitalcare login[/bold cyan] to get started."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)

# ─── Auth: standalone top-level commands ─────────────────────────────────────

@app.command("login")
def _login():
    """Log in to CityCare with your email and password."""
    from cli.commands.auth_cmd import login
    login()


@app.command("signup")
def _signup():
    """Create a new patient account."""
    from cli.commands.auth_cmd import signup
    signup()


@app.command("logout")
def _logout():
    """Log out and remove your locally stored token."""
    from cli.commands.auth_cmd import logout
    logout()


@app.command("whoami")
def _whoami():
    """Show currently logged-in user info (decoded from JWT)."""
    from cli.commands.auth_cmd import whoami
    whoami()


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.command("dashboard")
def _dashboard():
    """Show clinic-wide appointment dashboard statistics."""
    from cli.services import api_client as client
    with ui.spinner("Fetching dashboard…"):
        result = client.get("/v1/dashboard")
    ui.dashboard_card(result)


# ─── Command groups ───────────────────────────────────────────────────────────

app.add_typer(hospitals_app, name="hospitals",     help="List hospitals or view hospital details.")
app.add_typer(slots_app,     name="slots",         help="Check available appointment slots.")
app.add_typer(book_app,      name="book",          help="Book a new appointment (interactive).")
app.add_typer(appointments_app, name="appointments", help="View your appointments.")
app.add_typer(prescriptions_app, name="prescriptions", help="View prescriptions and PDF links.")
app.add_typer(chat_app,      name="chat",          help="Chat with the CityCare AI assistant.")


if __name__ == "__main__":
    app()
