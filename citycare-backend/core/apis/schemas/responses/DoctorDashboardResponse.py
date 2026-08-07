from pydantic import BaseModel, Field


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