from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HospitalResponse(BaseModel):
    id: str
    name: str
    address: str
    phone: str
    owner_id: Optional[str] = None
    created_at: datetime


class HospitalListResponse(BaseModel):
    id: str
    name: str
    address: str
    phone: str


class DoctorOfHospitalResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    hospital_id: Optional[str] = None


class OwnerResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None


class HospitalAppointmentResponse(BaseModel):
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
