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
        Returns hospital-scoped today's/upcoming visits + full appointment list.
        """

        try:
            logging.info(
                "Calling DoctorController.get_dashboard"
            )

            payload = self._verify_doctor(authorization)
            doctor = await self.user_crud.get_by_id(payload["id"])

            hospital_name = None
            hospital_id = None

            if doctor and doctor.hospital_id:
                hospital_id = doctor.hospital_id
                hospital = await self.hospital_crud.get_by_id(hospital_id)
                if hospital:
                    hospital_name = hospital.name

            # ── Stats scoped to the doctor's hospital ──────────────────────
            total_patients = await self.user_crud.get_total_patients()

            if hospital_id:
                # Hospital appointments list
                raw_appointments = await self.appointment_crud.get_appointments_by_hospital(
                    hospital_id
                )

                today = date.today()

                todays_visits = sum(
                    1 for a in raw_appointments
                    if a.appointment_date == today
                )
                upcoming_visits = sum(
                    1 for a in raw_appointments
                    if a.appointment_date > today
                )

                # Build enriched appointment list
                appointments = []
                for appt in raw_appointments:
                    patient = await self.user_crud.get_by_id(appt.patient_id)
                    patient_name = (
                        f"{patient.first_name} {patient.last_name}"
                        if patient
                        else "Unknown Patient"
                    )
                    doctor_name = None
                    if appt.doctor_id:
                        doc = await self.user_crud.get_by_id(appt.doctor_id)
                        if doc:
                            doctor_name = f"{doc.first_name} {doc.last_name}"

                    appointments.append({
                        "id": str(appt.id),
                        "patient_id": appt.patient_id,
                        "patient_name": patient_name,
                        "hospital_id": appt.hospital_id,
                        "doctor_id": appt.doctor_id,
                        "doctor_name": doctor_name,
                        "reason": appt.reason,
                        "symptoms": appt.symptoms,
                        "temperature": appt.temperature,
                        "appointment_date": str(appt.appointment_date),
                        "slot": appt.slot,
                        "status": appt.status,
                    })
            else:
                todays_visits = await self.appointment_crud.get_todays_visits()
                upcoming_visits = await self.appointment_crud.get_upcoming_visits()
                appointments = []

            return {
                "total_patients": total_patients,
                "todays_visits": todays_visits,
                "upcoming_visits": upcoming_visits,
                "hospital_name": hospital_name,
                "hospital_id": hospital_id,
                "appointments": appointments,
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