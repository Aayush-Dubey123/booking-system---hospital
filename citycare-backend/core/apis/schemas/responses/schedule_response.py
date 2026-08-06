from datetime import date

from pydantic import BaseModel


class ScheduleResponse(BaseModel):
    appointment_date: date
    booked_slots: list[str]
    free_slots: list[str]
    total_slots: int
    available_count: int
    booked_count: int
