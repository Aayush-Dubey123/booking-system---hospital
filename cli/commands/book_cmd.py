"""
book_cmd.py — Interactive appointment booking wizard.

Guides the patient step-by-step: hospital → date → slot → details → confirm.
Patient identity is taken exclusively from the JWT — no patient_id prompt.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import typer

import cli.auth as token_store
from cli.services import api_client as client
import cli.ui as ui

book_app = typer.Typer(
    name="book",
    help="Book a new appointment (interactive wizard).",
    no_args_is_help=False,
)

# Valid slots as defined in AppointmentController
VALID_SLOTS = [
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
]


@book_app.callback(invoke_without_command=True)
def book(ctx: typer.Context):
    """
    Interactively book a new appointment at a CityCare hospital.
    """
    if ctx.invoked_subcommand:
        return
    auth = token_store.require_auth()

    ui.console.print(
        "\n[bold cyan]📅  Book a New Appointment[/bold cyan]\n"
        "[dim]  We'll guide you through each step.[/dim]\n"
    )

    # ── Step 1: Choose hospital ───────────────────────────────────────────
    with ui.spinner("Loading hospitals…"):
        hospitals = client.get("/v1/hospitals")

    if not hospitals:
        ui.error_exit("No hospitals available right now. Please try again later.")

    hospital_labels = [f"{h['name']} — {h['address']}" for h in hospitals]
    idx = ui.pick_from_list("Step 1 of 4 · Choose a hospital:", hospital_labels)
    selected_hospital = hospitals[idx]
    hospital_id = selected_hospital["id"]
    ui.console.print(f"  [green]✓[/green] Selected: [bold]{selected_hospital['name']}[/bold]\n")

    # ── Step 2: Choose date ───────────────────────────────────────────────
    ui.console.print("[bold cyan]Step 2 of 4 · Choose a date[/bold cyan]")
    ui.console.print(
        f"  [dim]Appointments can be booked today up to 7 days ahead "
        f"({date.today().isoformat()} – {(date.today() + timedelta(days=7)).isoformat()})[/dim]"
    )
    while True:
        date_str = ui.prompt("Appointment date (YYYY-MM-DD)", default=date.today().isoformat())
        try:
            appt_date = date.fromisoformat(date_str)
        except ValueError:
            ui.console.print("  [red]Invalid date format. Use YYYY-MM-DD.[/red]")
            continue
        if appt_date < date.today():
            ui.console.print("  [red]Date cannot be in the past.[/red]")
            continue
        if appt_date > date.today() + timedelta(days=7):
            ui.console.print("  [red]Date must be within the next 7 days.[/red]")
            continue
        break

    # Show availability for the selected hospital & date
    with ui.spinner(f"Checking slots for {date_str} at {selected_hospital['name']}…"):
        schedule = client.get("/v1/schedule", params={
            "appointment_date": date_str,
            "hospital_id": hospital_id,
        })

    free_slots = schedule.get("free_slots", [])
    if not free_slots:
        ui.error_exit(
            f"No free slots available at [bold]{selected_hospital['name']}[/bold] on {date_str}.\n"
            "   Try a different date."
        )

    ui.console.print(f"\n  [green]✓[/green] Date: [bold]{date_str}[/bold]\n")

    # ── Step 3: Choose slot ───────────────────────────────────────────────
    slot_idx = ui.pick_from_list("Step 3 of 4 · Choose a time slot:", free_slots)
    selected_slot = free_slots[slot_idx]
    ui.console.print(f"  [green]✓[/green] Slot: [bold]{selected_slot}[/bold]\n")

    # ── Step 4: Reason, symptoms, temperature ────────────────────────────
    ui.console.print("[bold cyan]Step 4 of 4 · Medical details[/bold cyan]")
    reason = ui.prompt("Reason for visit")
    symptoms = ui.prompt("Symptoms")
    while True:
        temp_str = ui.prompt("Body temperature (°C)", default="37.0")
        try:
            temperature = float(temp_str)
            if not (30.0 <= temperature <= 45.0):
                raise ValueError
            break
        except ValueError:
            ui.console.print("  [red]Please enter a valid temperature (e.g. 37.5).[/red]")

    # ── Confirm ───────────────────────────────────────────────────────────
    ui.console.print(
        f"\n[bold]Confirm Appointment:[/bold]\n"
        f"  Hospital : [cyan]{selected_hospital['name']}[/cyan]\n"
        f"  Date     : [cyan]{date_str}[/cyan]\n"
        f"  Slot     : [cyan]{selected_slot}[/cyan]\n"
        f"  Reason   : {reason}\n"
        f"  Symptoms : {symptoms}\n"
        f"  Temp     : {temperature} °C"
    )

    if not ui.confirm("Book this appointment?"):
        ui.warning("Booking cancelled.")
        raise typer.Exit()

    payload = {
        "hospital_id": hospital_id,
        "appointment_date": date_str,
        "slot": selected_slot,
        "reason": reason,
        "symptoms": symptoms,
        "temperature": temperature,
    }

    with ui.spinner("Booking appointment…"):
        result = client.post("/v1/appointments/book", payload, auth=auth)

    ui.console.print()
    ui.success(
        f"Appointment booked! [bold]ID:[/bold] {result.get('id', 'N/A')} · "
        f"Status: [yellow]{result.get('status', 'pending')}[/yellow]"
    )
    ui.info("A doctor will accept your appointment shortly. Check status with [cyan]hospitalcare appointments[/cyan].")
