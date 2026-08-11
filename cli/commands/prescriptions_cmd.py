"""
prescriptions_cmd.py — View prescriptions and access PDF URLs.

Routes:
  GET /v1/prescriptions/my                      → prescriptions list
  GET /v1/prescriptions/{id}                    → single prescription detail
  GET /v1/prescriptions/appointment/{appt_id}  → prescription by appointment

Identity comes exclusively from the JWT.
"""
from __future__ import annotations

import typer

import cli.auth as token_store
from cli.services import api_client as client
import cli.ui as ui

prescriptions_app = typer.Typer(
    name="prescriptions",
    help="View your prescriptions and PDF links.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@prescriptions_app.callback(invoke_without_command=True)
def prescriptions_list(ctx: typer.Context):
    """
    List all your prescriptions.
    """
    if ctx.invoked_subcommand:
        return

    auth = token_store.require_auth()

    with ui.spinner("Fetching your prescriptions…"):
        result = client.get("/v1/prescriptions/my", auth=auth)

    if not result:
        ui.warning("No prescriptions found.")
        ui.info("Prescriptions are created by your doctor after an accepted appointment.")
        return

    ui.prescriptions_table(result)
    ui.console.print(
        f"\n  [dim]{len(result)} prescription(s).[/dim]  "
        "Use [cyan]hospitalcare prescriptions view <id>[/cyan] to see full details."
    )


@prescriptions_app.command("view")
def view_prescription(
    prescription_id: str = typer.Argument(..., help="Prescription ID"),
):
    """
    View full detail of a prescription (including PDF URL).
    """
    auth = token_store.require_auth()

    with ui.spinner(f"Fetching prescription {prescription_id}…"):
        result = client.get(f"/v1/prescriptions/{prescription_id}", auth=auth)

    ui.prescription_card(result)

    pdf_url = result.get("pdf_url")
    if pdf_url:
        ui.console.print(
            f"\n  [bold cyan]📄 Open PDF:[/bold cyan]\n"
            f"  {pdf_url}\n"
        )
        # Optionally open in browser
        if ui.confirm("Open PDF in browser?", default=False):
            import webbrowser
            webbrowser.open(pdf_url)
            ui.success("PDF opened in your default browser.")


@prescriptions_app.command("for-appointment")
def prescription_by_appointment(
    appointment_id: str = typer.Argument(..., help="Appointment ID"),
):
    """
    View the prescription for a specific appointment.
    """
    auth = token_store.require_auth()

    with ui.spinner(f"Fetching prescription for appointment {appointment_id}…"):
        result = client.get(f"/v1/prescriptions/appointment/{appointment_id}", auth=auth)

    ui.prescription_card(result)

    pdf_url = result.get("pdf_url")
    if pdf_url:
        ui.console.print(f"\n  [bold cyan]📄 PDF URL:[/bold cyan]\n  {pdf_url}\n")
        if ui.confirm("Open PDF in browser?", default=False):
            import webbrowser
            webbrowser.open(pdf_url)
            ui.success("PDF opened in your default browser.")
