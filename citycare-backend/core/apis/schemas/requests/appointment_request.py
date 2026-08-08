from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class AppointmentRequest(BaseModel):
    hospital_id: str = Field(
        ...,
        description="Hospital to book the appointment at."
    )

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