from datetime import date, datetime, timedelta

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


class AppointmentCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def create_appointment(self, appointment: dict) -> Appointment:
        try:
            logging.info("Creating a new appointment")
            return await self.engine.save(
                Appointment(**appointment)
            )
        except Exception as error:
            logging.error(f"Error creating appointment: {error}")
            raise

    async def get_appointments_by_date(
        self,
        appointment_date: date,
    ) -> list[Appointment]:
        try:
            logging.info(
                f"Finding appointments for date: {appointment_date}"
            )

            appointment_datetime = _date_to_datetime(
                appointment_date
            )

            return await self.engine.find(
                Appointment,
                Appointment.appointment_date == appointment_datetime,
            )

        except Exception as error:
            logging.error(f"Error finding appointments: {error}")
            raise

    async def get_patient_appointments(
        self,
        patient_id: str,
    ) -> list[Appointment]:
        try:
            logging.info(
                f"Finding appointments for patient: {patient_id}"
            )

            return await self.engine.find(
                Appointment,
                Appointment.patient_id == patient_id,
            )

        except Exception as error:
            logging.error(
                f"Error finding patient appointments: {error}"
            )
            raise

    async def get_todays_visits(self) -> int:
        try:
            logging.info("Fetching today's visits")

            today = _date_to_datetime(date.today())

            appointments = await self.engine.find(
                Appointment,
                Appointment.appointment_date == today,
            )

            return len(appointments)

        except Exception as error:
            logging.error(
                f"Error fetching today's visits: {error}"
            )
            raise

    async def get_upcoming_visits(self) -> int:
        try:
            logging.info("Fetching upcoming visits")

            today = _date_to_datetime(date.today())

            appointments = await self.engine.find(
                Appointment,
                Appointment.appointment_date > today,
            )

            return len(appointments)

        except Exception as error:
            logging.error(
                f"Error fetching upcoming visits: {error}"
            )
            raise

    async def get_schedule_by_date(
        self,
        appointment_date: date,
    ) -> list[Appointment]:
        try:
            logging.info(
                f"Fetching doctor schedule for date: {appointment_date}"
            )

            appointment_datetime = _date_to_datetime(
                appointment_date
            )

            return await self.engine.find(
                Appointment,
                Appointment.appointment_date == appointment_datetime,
            )

        except Exception as error:
            logging.error(
                f"Error fetching doctor schedule: {error}"
            )
            raise