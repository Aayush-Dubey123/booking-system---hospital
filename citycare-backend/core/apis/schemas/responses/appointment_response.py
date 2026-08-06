from datetime import date

from pydantic import BaseModel


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    appointment_date: date
    slot: str
    status: str
