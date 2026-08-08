from datetime import datetime,date
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    status: str
    created_at: datetime


class UserLoginResponse(BaseModel):
    access_token: str
    role: str
    hospital_id: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    appointment_date: date
    slot: str
    status: str

class MyAppointmentResponse(BaseModel):
    id: str
    patient_id: str
    reason: str
    symptoms: str
    temperature: float
    appointment_date: date
    slot: str
    status: str
    created_at: datetime

class DashboardResponse(BaseModel):
    total_appointments: int
    booked_appointments: int
    todays_appointments: int
    todays_free_slots: int
    todays_booked_slots: int
    total_slots_per_day: int

class ScheduleResponse(BaseModel):
    appointment_date: date
    booked_slots: list[str]
    free_slots: list[str]
    total_slots: int
    available_count: int
    booked_count: int    
