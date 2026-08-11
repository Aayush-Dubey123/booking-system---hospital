"""
hospital_cmd.py — Hospital listing and detail commands.
"""

from __future__ import annotations

import typer

from cli.services import api_client as client
import cli.ui as ui


hospitals_app = typer.Typer(
    name="hospitals",
    help="List hospitals or view a hospital's details.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@hospitals_app.callback(invoke_without_command=True)
def hospitals_list(ctx: typer.Context):
    """
    List all hospitals. (Default action — no subcommand needed.)
    """
    if ctx.invoked_subcommand:
        return

    try:
        with ui.spinner("Fetching hospitals..."):
            result = client.get("/v1/hospitals")

        ui.hospitals_table(result)

    except Exception as error:
        ui.error_exit(f"Unable to fetch hospitals: {error}")


@hospitals_app.command("info")
def hospital_info(
    hospital_id: str = typer.Argument(..., help="Hospital ID"),
):
    """
    View details of a specific hospital.
    """
    try:
        with ui.spinner(f"Fetching hospital {hospital_id}..."):
            result = client.get(f"/v1/hospitals/{hospital_id}")

        ui.hospital_card(result)

    except Exception as error:
        ui.error_exit(
            f"Unable to fetch hospital '{hospital_id}': {error}"
        )