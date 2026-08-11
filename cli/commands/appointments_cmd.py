"""
appointments_cmd.py — View patient appointments.

Identity comes exclusively from the JWT — no patient_id accepted from CLI.
"""
from __future__ import annotations

from typing import Optional

import typer

import cli.auth as token_store
from cli.services import api_client as client
import cli.ui as ui

appointments_app = typer.Typer(
    name="appointments",
    help="View your appointments.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@appointments_app.callback(invoke_without_command=True)
def appointments(ctx: typer.Context):
    """
    List all your appointments (most recent first).
    """
    if ctx.invoked_subcommand:
        return

    auth = token_store.require_auth()

    with ui.spinner("Fetching your appointments…"):
        result = client.get("/v1/appointments/my", auth=auth)

    if not result:
        ui.warning("You have no appointments yet. Book one with [cyan]hospitalcare book[/cyan].")
        return

    # Sort most-recent first
    try:
        result_sorted = sorted(result, key=lambda a: a.get("appointment_date", ""), reverse=True)
    except Exception:
        result_sorted = result

    ui.appointments_table(result_sorted)
    ui.console.print(
        f"\n  [dim]{len(result)} appointment(s) found.[/dim]  "
        "Run [cyan]hospitalcare prescriptions[/cyan] to view prescriptions."
    )
