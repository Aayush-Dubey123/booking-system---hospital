from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


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


class DoctorAppointmentItem(BaseModel):
    id: str
    patient_id: str
    patient_name: Optional[str] = None
    hospital_id: Optional[str] = None
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    reason: str
    symptoms: str
    temperature: float
    appointment_date: str
    slot: str
    status: str


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

    hospital_name: Optional[str] = Field(
        None,
        description="Name of the hospital the doctor belongs to."
    )

    hospital_id: Optional[str] = Field(
        None,
        description="Hospital ID the doctor belongs to."
    )

    appointments: List[DoctorAppointmentItem] = Field(
        default=[],
        description="All appointments for the doctor's hospital."
    )