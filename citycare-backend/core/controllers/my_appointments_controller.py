from fastapi import HTTPException, status

from core.cruds.appointment_crud import AppointmentCRUD
from common.auth import decodeJWT
from common.logger import logger

logging = logger(__name__)


class MyAppointmentsController:
    def __init__(self) -> None:
        self.appointment_crud = AppointmentCRUD()

    async def get_my_appointments(self, authorization: str) -> list:
        try:
            logging.info("Calling MyAppointmentsController.get_my_appointments")

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
                f"Error in MyAppointmentsController.get_my_appointments: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching appointments.",
            )
