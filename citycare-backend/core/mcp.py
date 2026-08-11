"""
core/mcp.py — FastMCP 3.4.5 tools and server definition for HospitalCare.

Exposes HospitalCare capabilities as standardized MCP tools by reusing
existing FastAPI controllers, validation, and database access logic directly.
"""

from datetime import date
from typing import Annotated, Any, Dict, List, Optional
from pydantic import Field
from fastmcp import FastMCP

from core.controllers.user_controller import UserController
from core.controllers.hospital_controller import HospitalController
from core.controllers.appointment_controller import AppointmentController
from core.controllers.doctor_controller import DoctorController
from core.controllers.prescription_controller import PrescriptionController
from core.controllers.chatbot_controller import ChatbotController
from core.controllers.dashboard_controller import DashboardController

mcp = FastMCP("HospitalCare")


def _format_auth(authorization: str) -> str:
    """Ensure authorization string starts with 'Bearer '."""
    if not authorization:
        return ""
    if not authorization.startswith("Bearer "):
        return f"Bearer {authorization}"
    return authorization


# ===================================================================
# AUTHENTICATION TOOLS
# ===================================================================

@mcp.tool(
    name="signup",
    description="Create a new HospitalCare patient account."
)
async def signup(
    first_name: Annotated[str, Field(description="Patient's first name", min_length=1, max_length=50)],
    last_name: Annotated[str, Field(description="Patient's last name", min_length=1, max_length=50)],
    email: Annotated[str, Field(description="Patient's email address")],
    password: Annotated[str, Field(description="Patient's account password")],
) -> Any:
    return await UserController().register_user({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
    })


@mcp.tool(
    name="login",
    description="Authenticate a HospitalCare user (patient/doctor/admin) and receive a JWT access token."
)
async def login(
    email: Annotated[str, Field(description="Registered email address")],
    password: Annotated[str, Field(description="Account password")],
) -> Any:
    return await UserController().login_user({
        "email": email,
        "password": password,
    })


# ===================================================================
# HOSPITAL & DOCTOR TOOLS
# ===================================================================

@mcp.tool(
    name="list_hospitals",
    description="List all hospitals registered in HospitalCare."
)
async def list_hospitals() -> Any:
    return await HospitalController().list_hospitals()


@mcp.tool(
    name="get_hospital",
    description="Get details of a specific hospital by its ID."
)
async def get_hospital(
    hospital_id: Annotated[str, Field(description="Unique ID of the hospital")]
) -> Any:
    return await HospitalController().get_hospital(hospital_id)


@mcp.tool(
    name="get_hospital_doctors",
    description="Get list of doctors operating at a specific hospital (requires authorization token)."
)
async def get_hospital_doctors(
    hospital_id: Annotated[str, Field(description="Unique ID of the hospital")],
    authorization: Annotated[str, Field(description="JWT authorization token (or 'Bearer <token>')")]
) -> Any:
    return await HospitalController().get_hospital_doctors(hospital_id, _format_auth(authorization))


# ===================================================================
# APPOINTMENT TOOLS
# ===================================================================

@mcp.tool(
    name="book_appointment",
    description="Book a doctor appointment at a hospital (requires patient authorization token)."
)
async def book_appointment(
    hospital_id: Annotated[str, Field(description="ID of the hospital")],
    doctor_id: Annotated[str, Field(description="ID of the doctor")],
    appointment_date: Annotated[str, Field(description="Appointment date in YYYY-MM-DD format")],
    slot: Annotated[str, Field(description="Time slot (e.g., '10:00', '11:30', '17:00')")],
    authorization: Annotated[str, Field(description="Patient JWT token (or 'Bearer <token>')")],
    reason: Annotated[Optional[str], Field(description="Optional reason for the appointment")] = "",
) -> Any:
    parsed_date = date.fromisoformat(appointment_date) if isinstance(appointment_date, str) else appointment_date
    return await AppointmentController().book_appointment(
        {
            "hospital_id": hospital_id,
            "doctor_id": doctor_id,
            "appointment_date": parsed_date,
            "slot": slot,
            "reason": reason or "",
        },
        _format_auth(authorization)
    )


@mcp.tool(
    name="get_my_appointments",
    description="Get appointments for the authenticated user (requires patient authorization token)."
)
async def get_my_appointments(
    authorization: Annotated[str, Field(description="JWT authorization token (or 'Bearer <token>')")]
) -> Any:
    return await AppointmentController().get_my_appointments(_format_auth(authorization))


@mcp.tool(
    name="get_schedule",
    description="Get appointment schedule / slot availability for a specific date (YYYY-MM-DD)."
)
async def get_schedule(
    appointment_date: Annotated[str, Field(description="Date to check in YYYY-MM-DD format")]
) -> Any:
    parsed_date = date.fromisoformat(appointment_date) if isinstance(appointment_date, str) else appointment_date
    return await AppointmentController().get_schedule(parsed_date)


# ===================================================================
# PRESCRIPTION TOOLS
# ===================================================================

@mcp.tool(
    name="get_my_prescriptions",
    description="Get prescriptions issued to the authenticated patient (requires authorization token)."
)
async def get_my_prescriptions(
    authorization: Annotated[str, Field(description="Patient JWT token (or 'Bearer <token>')")]
) -> Any:
    return await PrescriptionController().get_my_prescriptions(_format_auth(authorization))


@mcp.tool(
    name="get_prescription_by_id",
    description="Get details of a specific prescription by its ID (requires authorization token)."
)
async def get_prescription_by_id(
    prescription_id: Annotated[str, Field(description="ID of the prescription")],
    authorization: Annotated[str, Field(description="JWT authorization token (or 'Bearer <token>')")]
) -> Any:
    return await PrescriptionController().get_prescription_by_id(prescription_id, _format_auth(authorization))


@mcp.tool(
    name="get_prescription_by_appointment",
    description="Get prescription associated with a specific appointment ID (requires authorization token)."
)
async def get_prescription_by_appointment(
    appointment_id: Annotated[str, Field(description="ID of the appointment")],
    authorization: Annotated[str, Field(description="JWT authorization token (or 'Bearer <token>')")]
) -> Any:
    return await PrescriptionController().get_prescription_by_appointment(appointment_id, _format_auth(authorization))


@mcp.tool(
    name="create_prescription",
    description="Create a new medical prescription for an appointment (requires doctor authorization token)."
)
async def create_prescription(
    appointment_id: Annotated[str, Field(description="Appointment ID")],
    diagnosis: Annotated[str, Field(description="Medical diagnosis")],
    medicines: Annotated[str, Field(description="Prescribed medicines and dosage instructions")],
    authorization: Annotated[str, Field(description="Doctor JWT token (or 'Bearer <token>')")],
    notes: Annotated[Optional[str], Field(description="Optional additional notes")] = "",
) -> Any:
    return await PrescriptionController().create_prescription(
        {
            "appointment_id": appointment_id,
            "diagnosis": diagnosis,
            "medicines": medicines,
            "notes": notes or "",
        },
        _format_auth(authorization)
    )


# ===================================================================
# CHATBOT / HEALTH ASSISTANT TOOL
# ===================================================================

@mcp.tool(
    name="chat_with_health_assistant",
    description="Ask medical or booking questions to the HospitalCare RAG Health Assistant Chatbot."
)
async def chat_with_health_assistant(
    conversation_id: Annotated[str, Field(description="Unique conversation / session ID")],
    user_input: Annotated[str, Field(description="User message or health query")],
    authorization: Annotated[str, Field(description="User JWT token (or 'Bearer <token>')")]
) -> Any:
    reply = await ChatbotController().run_turn(
        conversation_id, user_input, _format_auth(authorization)
    )
    return {"response": reply}
