from pydantic import BaseModel, Field
from datetime import date


class DoctorScheduleResponse(BaseModel):
    patient_name: str = Field(
        ...,
        description="Patient full name."
    )

    appointment_date: date = Field(
        ...,
        description="Appointment date."
    )

    slot: str = Field(
        ...,
        description="Appointment slot."
    )

    reason: str = Field(
        ...,
        description="Reason for appointment."
    )

    symptoms: str = Field(
        ...,
        description="Patient symptoms."
    )

    temperature: float = Field(
        ...,
        description="Patient temperature."
    )

    status: str = Field(
        ...,
        description="Appointment status."
    )
    
class DoctorDashboardResponse(BaseModel):
    total_patients: int = Field(
        ...,
        description="Total registered patients."
    )

    todays_visits: int = Field(
        ...,
        description="Total appointments scheduled for today."
    )

    upcoming_visits: int = Field(
        ...,
        description="Total upcoming appointments."
    )    