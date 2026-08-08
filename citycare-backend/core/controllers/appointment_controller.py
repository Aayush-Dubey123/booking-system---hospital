from datetime import date, timedelta

from fastapi import HTTPException, status

from core.cruds.appointment_crud import AppointmentCRUD
from core.cruds.user_crud import UserCRUD
from core.cruds.hospital_crud import HospitalCRUD
from common.auth import decodeJWT
from common.auth_helpers import verify_token
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
        self.user_crud = UserCRUD()
        self.hospital_crud = HospitalCRUD()

    async def book_appointment(self, request: dict, authorization: str) -> dict:
        try:
            logging.info("Calling AppointmentController.book_appointment")

            payload = verify_token(authorization)
            request["patient_id"] = payload["id"]

            appointment_date = request.get("appointment_date")
            slot = request.get("slot")
            hospital_id = request.get("hospital_id")

            # Validate hospital exists
            if hospital_id:
                hospital = await self.hospital_crud.get_by_id(hospital_id)
                if not hospital:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Hospital not found.",
                    )

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

            # Check patient doesn't already have an appointment on this date
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

            # Auto-assign doctor: find first doctor of this hospital free on this slot
            assigned_doctor_id = None
            if hospital_id:
                doctors = await self.user_crud.get_doctors_by_hospital(hospital_id)
                if not doctors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No doctors available at this hospital.",
                    )

                for doctor in doctors:
                    booked_slots = (
                        await self.appointment_crud.get_doctor_booked_slots_on_date(
                            str(doctor.id), appointment_date
                        )
                    )
                    if slot not in booked_slots:
                        assigned_doctor_id = str(doctor.id)
                        break

                if not assigned_doctor_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected slot is fully booked at this hospital.",
                    )
            else:
                # Legacy path: no hospital — check global slot conflict
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

            request["doctor_id"] = assigned_doctor_id
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

            payload = verify_token(authorization)
            patient_id = payload["id"]

            appointments = await self.appointment_crud.get_patient_appointments(
                patient_id
            )

            logging.info(
                f"Found {len(appointments)} appointments for patient {patient_id}"
            )

            result = []
            for appointment in appointments:
                # Resolve hospital name
                hospital_name = None
                if appointment.hospital_id:
                    hospital = await self.hospital_crud.get_by_id(
                        appointment.hospital_id
                    )
                    if hospital:
                        hospital_name = hospital.name

                result.append(
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
                        "hospital_name": hospital_name,
                    }
                )

            return result

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

    async def get_schedule(self, appointment_date: date, hospital_id: str = None) -> dict:
        try:
            logging.info("Calling AppointmentController.get_schedule")

            if hospital_id:
                # Hospital-scoped: count slots booked across all doctors at this hospital
                appointments = (
                    await self.appointment_crud.get_appointments_by_hospital_and_date(
                        hospital_id, appointment_date
                    )
                )
                # Get doctors in this hospital
                doctors = await self.user_crud.get_doctors_by_hospital(hospital_id)
                num_doctors = max(len(doctors), 1)

                # A slot is "available" if at least one doctor is free for it
                booked_slots = []
                for slot in VALID_SLOTS:
                    bookings_for_slot = sum(
                        1 for a in appointments if a.slot == slot
                    )
                    if bookings_for_slot >= num_doctors:
                        booked_slots.append(slot)
            else:
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