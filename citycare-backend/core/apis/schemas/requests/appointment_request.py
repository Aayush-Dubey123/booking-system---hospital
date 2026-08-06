from datetime import date
from pydantic import BaseModel, Field


class AppointmentRequest(BaseModel):
    reason: str = Field(
        ...,
        description="Reason for booking the appointment."
    )

    symptoms: str = Field(
        ...,
        description="Symptoms experienced by the patient."
    )

    temperature: float = Field(
        ...,
        description="Patient's body temperature."
    )

    appointment_date: date = Field(
        ...,
        description="Appointment date."
    )

    slot: str = Field(
        ...,
        description="Preferred appointment slot."
    )