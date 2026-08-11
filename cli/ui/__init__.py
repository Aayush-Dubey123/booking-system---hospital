"""
cli/ui — Presentation and Rich components package.

Re-exports the full public UI API from console.py so command modules can use:
    from cli.ui import console, spinner, success, error_exit, hospitals_table, ...
or:
    from cli import ui
    ui.success("done")
"""
from cli.ui.console import (
    console,
    BRAND,
    print_banner,
    success,
    warning,
    info,
    error,
    error_exit,
    spinner,
    hospitals_table,
    hospital_card,
    slots_display,
    appointments_table,
    appointment_card,
    prescriptions_table,
    prescription_card,
    dashboard_card,
    prompt,
    confirm,
    pick_from_list,
)

__all__ = [
    "console",
    "BRAND",
    "print_banner",
    "success",
    "warning",
    "info",
    "error",
    "error_exit",
    "spinner",
    "hospitals_table",
    "hospital_card",
    "slots_display",
    "appointments_table",
    "appointment_card",
    "prescriptions_table",
    "prescription_card",
    "dashboard_card",
    "prompt",
    "confirm",
    "pick_from_list",
]
