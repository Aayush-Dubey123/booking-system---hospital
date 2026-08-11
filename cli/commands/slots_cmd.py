"""
slots_cmd.py — Check available appointment slots for a date.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import typer

from cli.services import api_client as client
import cli.ui as ui

slots_app = typer.Typer(
    name="slots",
    help="Check available appointment slots.",
    no_args_is_help=False,
)


@slots_app.callback(invoke_without_command=True)
def slots(
    ctx: typer.Context,
    appointment_date: Optional[str] = typer.Argument(
        None,
        help="Date to check (YYYY-MM-DD). Defaults to today.",
    ),
    hospital_id: Optional[str] = typer.Option(
        None,
        "--hospital",
        "-H",
        help="Filter by hospital ID.",
    ),
):
    """
    Show free and booked slots for a given date.

    Examples:
      hospitalcare slots
      hospitalcare slots 2026-08-15
      hospitalcare slots 2026-08-15 --hospital <id>
    """
    if ctx.invoked_subcommand:
        return

    if appointment_date is None:
        appointment_date = date.today().isoformat()

    params: dict = {"appointment_date": appointment_date}
    if hospital_id:
        params["hospital_id"] = hospital_id

    with ui.spinner(f"Fetching slots for {appointment_date}…"):
        result = client.get("/v1/schedule", params=params)

    ui.slots_display(result)
