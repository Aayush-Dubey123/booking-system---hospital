from datetime import date, datetime
from typing import Annotated

from odmantic import Model, WithBsonSerializer


# BSON has no native date-only type — MongoDB only understands datetime (UTC).
# WithBsonSerializer tells ODMantic to convert date → datetime(y,m,d,0,0,0)
# before writing to MongoDB, preserving date-only semantics in Python.
DateField = Annotated[
    date,
    WithBsonSerializer(lambda v: datetime(v.year, v.month, v.day, 0, 0, 0)),
]


class Appointment(Model):
    patient_id: str
    reason: str
    symptoms: str
    temperature: float
    appointment_date: DateField
    slot: str
    status: str = "booked"
    created_at: datetime = datetime.utcnow()

    model_config = {
        "collection": "appointments",
    }