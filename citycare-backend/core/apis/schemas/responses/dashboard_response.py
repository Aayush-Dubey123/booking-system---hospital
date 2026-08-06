from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_appointments: int
    booked_appointments: int
    todays_appointments: int
    todays_free_slots: int
    todays_booked_slots: int
    total_slots_per_day: int
