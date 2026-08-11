from datetime import date, datetime, timedelta

from odmantic import AIOEngine, ObjectId
from core.database.database import get_engine, MongoDatabase
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

    async def get_by_id(self, appointment_id: str) -> Appointment | None:
        try:
            logging.info(f"Fetching appointment by ID: {appointment_id}")
            try:
                oid = ObjectId(appointment_id)
            except Exception:
                return None
            return await self.engine.find_one(Appointment, Appointment.id == oid)
        except Exception as error:
            logging.error(f"Error fetching appointment by ID: {error}")
            raise

    async def accept_appointment_atomic(self, appointment_id: str, doctor_id: str) -> Appointment | None:
        try:
            logging.info(f"Atomic update for appointment {appointment_id} acceptance by doctor {doctor_id}")
            db = MongoDatabase()
            try:
                oid = ObjectId(appointment_id)
            except Exception:
                return None

            result = await db["appointments"].find_one_and_update(
                {"_id": oid, "status": "pending"},
                {"$set": {"status": "accepted", "doctor_id": doctor_id}},
                return_document=True,
            )
            if not result:
                return None
            return await self.engine.find_one(Appointment, Appointment.id == oid)
        except Exception as error:
            logging.error(f"Error in accept_appointment_atomic: {error}")
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

    async def get_total_appointments(self) -> int:
        try:
            logging.info("Fetching total appointment count")
            appointments = await self.engine.find(Appointment)
            return len(appointments)
        except Exception as error:
            logging.error(f"Error fetching total appointments: {error}")
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

    async def get_appointments_by_hospital(
        self,
        hospital_id: str,
    ) -> list[Appointment]:
        try:
            logging.info(f"Fetching appointments for hospital: {hospital_id}")
            return await self.engine.find(
                Appointment,
                Appointment.hospital_id == hospital_id,
            )
        except Exception as error:
            logging.error(f"Error fetching hospital appointments: {error}")
            raise

    async def get_appointments_by_doctor(
        self,
        doctor_id: str,
    ) -> list[Appointment]:
        try:
            logging.info(f"Fetching appointments for doctor: {doctor_id}")
            return await self.engine.find(
                Appointment,
                Appointment.doctor_id == doctor_id,
            )
        except Exception as error:
            logging.error(f"Error fetching doctor appointments: {error}")
            raise

    async def get_appointments_by_hospital_and_date(
        self,
        hospital_id: str,
        appointment_date: date,
    ) -> list[Appointment]:
        try:
            logging.info(
                f"Fetching appointments for hospital {hospital_id} on {appointment_date}"
            )
            appointment_datetime = _date_to_datetime(appointment_date)
            return await self.engine.find(
                Appointment,
                (Appointment.hospital_id == hospital_id)
                & (Appointment.appointment_date == appointment_datetime),
            )
        except Exception as error:
            logging.error(f"Error fetching hospital-date appointments: {error}")
            raise

    async def get_doctor_booked_slots_on_date(
        self,
        doctor_id: str,
        appointment_date: date,
    ) -> list[str]:
        try:
            logging.info(
                f"Fetching booked slots for doctor {doctor_id} on {appointment_date}"
            )
            appointment_datetime = _date_to_datetime(appointment_date)
            appointments = await self.engine.find(
                Appointment,
                (Appointment.doctor_id == doctor_id)
                & (Appointment.appointment_date == appointment_datetime),
            )
            return [a.slot for a in appointments]
        except Exception as error:
            logging.error(f"Error fetching doctor booked slots: {error}")
            raise