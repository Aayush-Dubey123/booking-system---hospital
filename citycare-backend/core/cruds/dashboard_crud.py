from datetime import date, datetime

from odmantic import AIOEngine

from core.database.database import get_engine
from core.models.appointment_model import Appointment
from common.logger import logger

logging = logger(__name__)


def _date_to_datetime(d: date) -> datetime:
    """
    BSON has no native date-only type.
    Convert a date to midnight datetime so queries match stored values.
    """
    return datetime(d.year, d.month, d.day, 0, 0, 0)


class DashboardCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def get_total_appointments(self) -> int:
        try:
            logging.info("Fetching total appointment count")
            appointments = await self.engine.find(Appointment)
            return len(appointments)
        except Exception as error:
            logging.error(f"Error fetching total appointments: {error}")
            raise

    async def get_appointments_by_date(
        self,
        appointment_date: date,
    ) -> list[Appointment]:
        try:
            logging.info(
                f"Fetching appointments for date: {appointment_date}"
            )

            appointment_datetime = _date_to_datetime(appointment_date)

            return await self.engine.find(
                Appointment,
                Appointment.appointment_date == appointment_datetime,
            )

        except Exception as error:
            logging.error(f"Error fetching appointments by date: {error}")
            raise

    async def get_appointments_by_status(
        self,
        status_value: str,
    ) -> int:
        try:
            logging.info(
                f"Fetching appointments with status: {status_value}"
            )

            appointments = await self.engine.find(
                Appointment,
                Appointment.status == status_value,
            )

            return len(appointments)

        except Exception as error:
            logging.error(
                f"Error fetching appointments by status: {error}"
            )
            raise