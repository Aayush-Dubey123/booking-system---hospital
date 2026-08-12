"""
cli/ui/console.py — Rich terminal components for HospitalCare CLI.

Provides reusable cards, tables, messages, spinners and confirmations.
"""
from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich import box

console = Console()


# ─── Branding ────────────────────────────────────────────────────────────────

BRAND = "[bold cyan] CityCare[/bold cyan]"


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]HospitalCare CLI[/bold cyan]\n"
            "[dim]  Terminal frontend for CityCare Clinic  [/dim]",
            border_style="cyan",
        )
    )


# ─── Status messages ──────────────────────────────────────────────────────────

def success(msg: str) -> None:
    console.print(f"[bold green]OK[/bold green]  {msg}")


def warning(msg: str) -> None:
    console.print(f"[bold yellow]WARNING[/bold yellow]  {msg}")


def info(msg: str) -> None:
    console.print(f"[dim]INFO[/dim]  {msg}")


def error(msg: str) -> None:
    console.print(f"[bold red]ERROR[/bold red]  {msg}")


def error_exit(msg: str, code: int = 1) -> None:
    """Print error and exit without a stack trace."""
    console.print(f"\n[bold red]ERROR[/bold red]  {msg}\n")
    sys.exit(code)


# ─── Spinner ─────────────────────────────────────────────────────────────────

@contextmanager
def spinner(message: str):
    """
    Windows-safe spinner/progress display.

    Uses plain ASCII-compatible output instead of Rich's
    Unicode Braille spinner characters.
    """
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )

    try:
        progress.start()
        progress.add_task(
            description=message,
            total=None,
        )
        yield
    finally:
        progress.stop()


# ─── Tables ──────────────────────────────────────────────────────────────────

def hospitals_table(hospitals: list[dict]) -> None:
    if not hospitals:
        warning("No hospitals found.")
        return
    table = Table(
        title="Hospitals",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("ID", style="dim cyan", no_wrap=True)
    table.add_column("Name", style="bold white")
    table.add_column("Address")
    table.add_column("Phone")
    for i, h in enumerate(hospitals, 1):
        table.add_row(str(i), h.get("id", ""), h.get("name", ""), h.get("address", ""), h.get("phone", ""))
    console.print(table)


def hospital_card(h: dict) -> None:
    body = (
        f"[bold]ID:[/bold]      {h.get('id', 'N/A')}\n"
        f"[bold]Name:[/bold]    {h.get('name', 'N/A')}\n"
        f"[bold]Address:[/bold] {h.get('address', 'N/A')}\n"
        f"[bold]Phone:[/bold]   {h.get('phone', 'N/A')}\n"
        f"[bold]Owner:[/bold]   {h.get('owner_id', 'N/A')}\n"
        f"[bold]Created:[/bold] {h.get('created_at', 'N/A')}"
    )
    console.print(Panel(body, title="Hospital Details", border_style="cyan"))


def slots_display(schedule: dict) -> None:
    date_str = schedule.get("appointment_date", "Unknown")
    free = schedule.get("free_slots", [])
    booked = schedule.get("booked_slots", [])

    console.print(
        Panel(
            f"[bold]Date:[/bold]      {date_str}\n"
            f"[bold]Available:[/bold] [green]{schedule.get('available_count', 0)}[/green] / "
            f"{schedule.get('total_slots', 0)} total",
            title="Slot Availability",
            border_style="cyan",
        )
    )

    if free:
        table = Table(box=box.SIMPLE, header_style="bold green", show_header=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Available Slot", style="bold green")
        table.add_column("Status")
        for i, slot in enumerate(free, 1):
            table.add_row(str(i), slot, "[green]FREE[/green]")
        for slot in booked:
            table.add_row("", slot, "[red]NO Booked[/red]")
        console.print(table)
    else:
        warning("No free slots available on this date.")


def appointments_table(appointments: list[dict]) -> None:
    if not appointments:
        warning("No appointments found.")
        return
    table = Table(
        title="My Appointments",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim cyan", no_wrap=True, max_width=24)
    table.add_column("Date", style="bold white")
    table.add_column("Slot")
    table.add_column("Hospital")
    table.add_column("Doctor")
    table.add_column("Status")
    table.add_column("Rx?", justify="center")

    for appt in appointments:
        status = appt.get("status", "")
        status_style = {
            "pending": "[yellow]pending[/yellow]",
            "accepted": "[green]accepted[/green]",
            "cancelled": "[red]cancelled[/red]",
            "completed": "[dim]completed[/dim]",
        }.get(status, status)

        has_rx = "YES" if appt.get("prescription") else "—"
        appt_id = appt.get("id", "")
        short_id = appt_id[:12] + "..." if len(appt_id) > 13 else appt_id

        table.add_row(
            short_id,
            str(appt.get("appointment_date", "")),
            appt.get("slot", ""),
            appt.get("hospital_name") or "—",
            appt.get("doctor_name") or "—",
            status_style,
            has_rx,
        )
    console.print(table)


def appointment_card(appt: dict) -> None:
    lines = [
        f"[bold]ID:[/bold]      {appt.get('id', 'N/A')}",
        f"[bold]Date:[/bold]    {appt.get('appointment_date', 'N/A')}",
        f"[bold]Slot:[/bold]    {appt.get('slot', 'N/A')}",
        f"[bold]Hospital:[/bold] {appt.get('hospital_name') or 'N/A'}",
        f"[bold]Doctor:[/bold]  {appt.get('doctor_name') or 'Not assigned yet'}",
        f"[bold]Status:[/bold]  {appt.get('status', 'N/A')}",
        f"[bold]Reason:[/bold]  {appt.get('reason', 'N/A')}",
        f"[bold]Symptoms:[/bold] {appt.get('symptoms', 'N/A')}",
        f"[bold]Temp:[/bold]    {appt.get('temperature', 'N/A')} °C",
    ]
    if appt.get("prescription"):
        rx = appt["prescription"]
        lines.append(f"\n[bold green]Prescription available[/bold green]")
        lines.append(f"   Diagnosis: {rx.get('diagnosis', 'N/A')}")
        lines.append(f"   PDF: {rx.get('pdf_url', 'N/A')}")
    console.print(Panel("\n".join(lines), title="Appointment Detail", border_style="cyan"))


def prescriptions_table(prescriptions: list[dict]) -> None:
    if not prescriptions:
        warning("No prescriptions found.")
        return
    table = Table(
        title="My Prescriptions",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim cyan", no_wrap=True, max_width=24)
    table.add_column("Date")
    table.add_column("Doctor")
    table.add_column("Diagnosis", max_width=30)
    table.add_column("Medicines", max_width=35)
    table.add_column("PDF", style="cyan")

    for p in prescriptions:
        p_id = p.get("id", "")
        short_id = p_id[:12] + "..." if len(p_id) > 13 else p_id
        pdf = "Available" if p.get("pdf_url") else "—"
        table.add_row(
            short_id,
            str(p.get("created_at", ""))[:10],
            p.get("doctor_name") or "—",
            p.get("diagnosis", "")[:30],
            p.get("medicines", "")[:35],
            pdf,
        )
    console.print(table)


def prescription_card(p: dict) -> None:
    body = (
        f"[bold]ID:[/bold]           {p.get('id', 'N/A')}\n"
        f"[bold]Appointment:[/bold]  {p.get('appointment_id', 'N/A')}\n"
        f"[bold]Patient:[/bold]      {p.get('patient_name', 'N/A')}\n"
        f"[bold]Doctor:[/bold]       {p.get('doctor_name', 'N/A')}\n"
        f"[bold]Date:[/bold]         {str(p.get('created_at', 'N/A'))[:10]}\n\n"
        f"[bold yellow]Diagnosis:[/bold yellow]\n  {p.get('diagnosis', 'N/A')}\n\n"
        f"[bold yellow]Medicines:[/bold yellow]\n  {p.get('medicines', 'N/A')}\n\n"
        f"[bold yellow]Notes:[/bold yellow]\n  {p.get('notes') or '—'}\n\n"
        f"[bold cyan]PDF URL:[/bold cyan]\n  {p.get('pdf_url') or '—'}"
    )
    console.print(Panel(body, title="Prescription Detail", border_style="green"))


def dashboard_card(d: dict) -> None:
    body = (
        f"[bold]Total Appointments:[/bold]   {d.get('total_appointments', 0)}\n"
        f"[bold]Booked Appointments:[/bold]  {d.get('booked_appointments', 0)}\n"
        f"[bold]Today's Appointments:[/bold] {d.get('todays_appointments', 0)}\n"
        f"[bold]Today's Free Slots:[/bold]   [green]{d.get('todays_free_slots', 0)}[/green]\n"
        f"[bold]Today's Booked Slots:[/bold] {d.get('todays_booked_slots', 0)}\n"
        f"[bold]Total Slots / Day:[/bold]    {d.get('total_slots_per_day', 0)}"
    )
    console.print(Panel(body, title="Dashboard", border_style="cyan"))


# ─── Prompts ─────────────────────────────────────────────────────────────────

def prompt(label: str, default: Optional[str] = None, password: bool = False) -> str:
    return Prompt.ask(f"  [cyan]{label}[/cyan]", default=default, password=password)


def confirm(question: str, default: bool = True) -> bool:
    return Confirm.ask(f"  [cyan]{question}[/cyan]", default=default)


def pick_from_list(title: str, items: list[str]) -> int:
    """Show a numbered list and return the 0-based index of user choice."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    for i, item in enumerate(items, 1):
        console.print(f"  [dim]{i}.[/dim]  {item}")
    while True:
        choice = Prompt.ask(f"  Enter number [1-{len(items)}]")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return idx
        except ValueError:
            pass
        console.print(f"  [red]Please enter a number between 1 and {len(items)}.[/red]")
