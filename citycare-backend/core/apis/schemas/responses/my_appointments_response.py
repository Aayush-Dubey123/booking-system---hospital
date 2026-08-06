from datetime import date, datetime

from pydantic import BaseModel


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
