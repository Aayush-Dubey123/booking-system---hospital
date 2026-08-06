from datetime import date, datetime

from odmantic import AIOEngine

from core.database.database import get_engine
from core.models.appointment_model import Appointment
from common.logger import logger

logging = logger(__name__)


def _date_to_datetime(d: date) -> datetime:
    """
    Convert a Python date into a datetime at midnight.
    MongoDB stores BSON datetime values, not date-only values.
    """
    return datetime(d.year, d.month, d.day, 0, 0, 0)


class ScheduleCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def get_booked_slots(
        self,
        appointment_date: date,
    ) -> list[str]:
        try:
            logging.info(
                f"Fetching booked slots for date: {appointment_date}"
            )

            appointment_datetime = _date_to_datetime(appointment_date)

            appointments = await self.engine.find(
                Appointment,
                Appointment.appointment_date == appointment_datetime,
            )

            return [appointment.slot for appointment in appointments]

        except Exception as error:
            logging.error(f"Error fetching booked slots: {error}")
            raise