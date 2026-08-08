from datetime import date

from fastapi import HTTPException, status

from common.auth_helpers import verify_token, require_role
from common.logger import logger
from core.cruds.user_crud import UserCRUD
from core.cruds.appointment_crud import AppointmentCRUD
from core.cruds.hospital_crud import HospitalCRUD

logging = logger(__name__)


class DoctorController:
    def __init__(self) -> None:
        self.user_crud = UserCRUD()
        self.appointment_crud = AppointmentCRUD()
        self.hospital_crud = HospitalCRUD()

    def _verify_doctor(self, authorization: str) -> dict:
        """
        Verify JWT token and ensure user is a doctor.
        """
        payload = verify_token(authorization)
        require_role(payload, "doctor")
        return payload

    async def get_dashboard(
        self,
        authorization: str,
    ) -> dict:
        """
        Doctor dashboard statistics — scoped to doctor's hospital.
        """

        try:
            logging.info(
                "Calling DoctorController.get_dashboard"
            )

            payload = self._verify_doctor(authorization)
            doctor = await self.user_crud.get_by_id(payload["id"])

            # Get hospital info
            hospital_name = None
            if doctor and doctor.hospital_id:
                hospital = await self.hospital_crud.get_by_id(doctor.hospital_id)
                if hospital:
                    hospital_name = hospital.name

            total_patients = (
                await self.user_crud.get_total_patients()
            )

            todays_visits = (
                await self.appointment_crud.get_todays_visits()
            )

            upcoming_visits = (
                await self.appointment_crud.get_upcoming_visits()
            )

            return {
                "total_patients": total_patients,
                "todays_visits": todays_visits,
                "upcoming_visits": upcoming_visits,
                "hospital_name": hospital_name,
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(
                f"Error in DoctorController.get_dashboard: {error}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching doctor dashboard.",
            )

    async def get_schedule(
        self,
        appointment_date: date,
        authorization: str,
    ) -> list[dict]:
        """
        Doctor schedule for a given day — scoped to doctor's own appointments.
        """

        try:
            logging.info(
                "Calling DoctorController.get_schedule"
            )

            payload = self._verify_doctor(authorization)
            doctor_id = payload["id"]

            # Get appointments assigned to this specific doctor on the date
            all_appointments = (
                await self.appointment_crud.get_schedule_by_date(
                    appointment_date
                )
            )

            # Filter to this doctor's appointments
            appointments = [
                a for a in all_appointments
                if a.doctor_id == doctor_id or a.doctor_id is None
            ]

            response = []

            for appointment in appointments:

                patient = await self.user_crud.get_by_id(
                    appointment.patient_id
                )

                if patient:
                    patient_name = (
                        f"{patient.first_name} {patient.last_name}"
                    )
                else:
                    patient_name = "Unknown Patient"

                response.append(
                    {
                        "patient_name": patient_name,
                        "appointment_date": appointment.appointment_date,
                        "slot": appointment.slot,
                        "reason": appointment.reason,
                        "symptoms": appointment.symptoms,
                        "temperature": appointment.temperature,
                        "status": appointment.status,
                    }
                )

            return response

        except HTTPException:
            raise

        except Exception as error:
            logging.error(
                f"Error in DoctorController.get_schedule: {error}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching doctor schedule.",
            )