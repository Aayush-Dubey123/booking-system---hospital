from datetime import date

from fastapi import HTTPException, status

from common.auth import decodeJWT
from common.logger import logger
from core.cruds.user_crud import UserCRUD
from core.cruds.appointment_crud import AppointmentCRUD

logging = logger(__name__)


class DoctorController:
    def __init__(self) -> None:
        self.user_crud = UserCRUD()
        self.appointment_crud = AppointmentCRUD()

    def _verify_doctor(self, authorization: str) -> dict:
        """
        Verify JWT token and ensure user is a doctor.
        """

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

        if payload.get("role") != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor access only.",
            )

        return payload

    async def get_dashboard(
        self,
        authorization: str,
    ) -> dict:
        """
        Doctor dashboard statistics.
        """

        try:
            logging.info(
                "Calling DoctorController.get_dashboard"
            )

            self._verify_doctor(authorization)

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
        Doctor schedule for a given day.
        """

        try:
            logging.info(
                "Calling DoctorController.get_schedule"
            )

            self._verify_doctor(authorization)

            appointments = (
                await self.appointment_crud.get_schedule_by_date(
                    appointment_date
                )
            )

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