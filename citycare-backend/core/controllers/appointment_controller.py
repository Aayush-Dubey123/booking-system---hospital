from datetime import date, timedelta

from fastapi import HTTPException, status

from core.cruds.appointment_crud import AppointmentCRUD
from common.auth import decodeJWT
from common.logger import logger

logging = logger(__name__)

VALID_SLOTS = [
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "17:00",
    "17:30",
    "18:00",
    "18:30",
    "19:00",
    "19:30",
]


class AppointmentController:
    def __init__(self) -> None:
        self.appointment_crud = AppointmentCRUD()

    async def book_appointment(self, request: dict, authorization: str) -> dict:
        try:
            logging.info("Calling AppointmentController.book_appointment")

            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header.",
                )

            token = authorization.split(" ")[1]

            payload = decodeJWT(token)

            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                )

            request["patient_id"] = payload["id"]

            appointment_date = request.get("appointment_date")
            slot = request.get("slot")

            today = date.today()

            if appointment_date < today:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Appointment date cannot be in the past.",
                )

            if appointment_date > today + timedelta(days=7):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Appointments can only be booked up to 7 days in advance.",
                )

            if slot not in VALID_SLOTS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid appointment slot.",
                )

            patient_appointments = (
                await self.appointment_crud.get_patient_appointments(
                    request["patient_id"]
                )
            )

            for appointment in patient_appointments:
                if appointment.appointment_date == appointment_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Patient already has an appointment on this date.",
                    )

            appointments = (
                await self.appointment_crud.get_appointments_by_date(
                    appointment_date
                )
            )

            for appointment in appointments:
                if appointment.slot == slot:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected slot is already booked.",
                    )

            appointment = await self.appointment_crud.create_appointment(request)

            logging.info("Appointment booked successfully")

            return {
                "id": str(appointment.id),
                "patient_id": appointment.patient_id,
                "appointment_date": appointment.appointment_date,
                "slot": appointment.slot,
                "status": appointment.status,
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(f"Error in AppointmentController.book_appointment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while booking the appointment.",
            )

    async def get_my_appointments(self, authorization: str) -> list:
        try:
            logging.info("Calling AppointmentController.get_my_appointments")

            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header.",
                )

            token = authorization.split(" ")[1]

            payload = decodeJWT(token)

            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                )

            patient_id = payload["id"]

            appointments = await self.appointment_crud.get_patient_appointments(
                patient_id
            )

            logging.info(
                f"Found {len(appointments)} appointments for patient {patient_id}"
            )

            return [
                {
                    "id": str(appointment.id),
                    "patient_id": appointment.patient_id,
                    "reason": appointment.reason,
                    "symptoms": appointment.symptoms,
                    "temperature": appointment.temperature,
                    "appointment_date": appointment.appointment_date,
                    "slot": appointment.slot,
                    "status": appointment.status,
                    "created_at": appointment.created_at,
                }
                for appointment in appointments
            ]

        except HTTPException:
            raise

        except Exception as error:
            logging.error(
                f"Error in AppointmentController.get_my_appointments: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching appointments.",
            )

    async def get_schedule(self, appointment_date: date) -> dict:
        try:
            logging.info("Calling AppointmentController.get_schedule")

            booked_slots = await self.appointment_crud.get_booked_slots(
                appointment_date
            )

            free_slots = [
                slot for slot in VALID_SLOTS if slot not in booked_slots
            ]

            logging.info(
                f"Schedule computed for {appointment_date}: "
                f"{len(booked_slots)} booked, {len(free_slots)} free"
            )

            return {
                "appointment_date": appointment_date,
                "booked_slots": booked_slots,
                "free_slots": free_slots,
                "total_slots": len(VALID_SLOTS),
                "available_count": len(free_slots),
                "booked_count": len(booked_slots),
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(f"Error in AppointmentController.get_schedule: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching the schedule.",
            )