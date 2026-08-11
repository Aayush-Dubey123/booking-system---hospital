from fastapi import HTTPException, status
from common.auth_helpers import verify_token, require_role
from common.logger import logger
from common.pdf_generator import generate_prescription_pdf
from common.cloudinary_service import upload_pdf_to_cloudinary
from core.cruds.appointment_crud import AppointmentCRUD
from core.cruds.prescription_crud import PrescriptionCRUD
from core.cruds.user_crud import UserCRUD

logging = logger(__name__)


class PrescriptionController:
    def __init__(self) -> None:
        self.prescription_crud = PrescriptionCRUD()
        self.appointment_crud = AppointmentCRUD()
        self.user_crud = UserCRUD()

    async def create_prescription(self, request_data: dict, authorization: str) -> dict:
        try:
            logging.info("Calling PrescriptionController.create_prescription")

            payload = verify_token(authorization)
            require_role(payload, "doctor")
            caller_doctor_id = payload["id"]

            appointment_id = request_data.get("appointment_id")
            diagnosis = request_data.get("diagnosis")
            medicines = request_data.get("medicines")
            notes = request_data.get("notes", "")

            if not appointment_id or not diagnosis or not medicines:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="appointment_id, diagnosis, and medicines are required.",
                )

            appointment = await self.appointment_crud.get_by_id(appointment_id)
            if not appointment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Appointment not found.",
                )

            if appointment.status != "accepted":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Prescription can only be created for accepted appointments.",
                )

            if appointment.doctor_id != caller_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the assigned doctor can create a prescription for this appointment.",
                )

            existing_p = await self.prescription_crud.get_by_appointment_id(appointment_id)
            if existing_p:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Prescription already exists for this appointment.",
                )

            patient = await self.user_crud.get_by_id(appointment.patient_id)
            doctor = await self.user_crud.get_by_id(caller_doctor_id)

            patient_name = (
                f"{patient.first_name} {patient.last_name}" if patient else "Patient"
            )
            doctor_name = (
                f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Doctor"
            )

            # Generate PDF
            pdf_bytes = generate_prescription_pdf(
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=str(appointment.appointment_date),
                slot=appointment.slot,
                diagnosis=diagnosis,
                medicines=medicines,
                notes=notes,
            )

            # Upload PDF to Cloudinary as raw PDF
            cloudinary_url = upload_pdf_to_cloudinary(
                pdf_bytes=pdf_bytes,
                filename=f"rx_{appointment_id}.pdf",
            )

            prescription_dict = {
                "appointment_id": appointment_id,
                "patient_id": appointment.patient_id,
                "doctor_id": caller_doctor_id,
                "diagnosis": diagnosis,
                "medicines": medicines,
                "notes": notes,
                "pdf_url": cloudinary_url,
            }

            prescription = await self.prescription_crud.create_prescription(prescription_dict)

            logging.info(f"Prescription created successfully for appointment {appointment_id}")

            return {
                "id": str(prescription.id),
                "appointment_id": prescription.appointment_id,
                "patient_id": prescription.patient_id,
                "patient_name": patient_name,
                "doctor_id": prescription.doctor_id,
                "doctor_name": doctor_name,
                "diagnosis": prescription.diagnosis,
                "medicines": prescription.medicines,
                "notes": prescription.notes,
                "pdf_url": prescription.pdf_url,
                "created_at": prescription.created_at,
            }

        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error creating prescription: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the prescription.",
            )

    async def get_my_prescriptions(self, authorization: str) -> list[dict]:
        try:
            logging.info("Calling PrescriptionController.get_my_prescriptions")
            payload = verify_token(authorization)
            user_id = payload["id"]
            role = payload.get("role")

            if role == "patient":
                prescriptions = await self.prescription_crud.get_by_patient_id(user_id)
            elif role == "doctor":
                prescriptions = await self.prescription_crud.get_by_doctor_id(user_id)
            else:
                prescriptions = []

            results = []
            for p in prescriptions:
                patient = await self.user_crud.get_by_id(p.patient_id)
                doctor = await self.user_crud.get_by_id(p.doctor_id)
                results.append({
                    "id": str(p.id),
                    "appointment_id": p.appointment_id,
                    "patient_id": p.patient_id,
                    "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Patient",
                    "doctor_id": p.doctor_id,
                    "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Doctor",
                    "diagnosis": p.diagnosis,
                    "medicines": p.medicines,
                    "notes": p.notes,
                    "pdf_url": p.pdf_url,
                    "created_at": p.created_at,
                })

            return results
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error fetching prescriptions: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching prescriptions.",
            )

    async def get_prescription_by_appointment(self, appointment_id: str, authorization: str) -> dict:
        try:
            logging.info(f"Fetching prescription for appointment: {appointment_id}")
            payload = verify_token(authorization)
            caller_id = payload["id"]

            p = await self.prescription_crud.get_by_appointment_id(appointment_id)
            if not p:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prescription not found for this appointment.",
                )

            # Strict authorization check
            if p.patient_id != caller_id and p.doctor_id != caller_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this prescription.",
                )

            patient = await self.user_crud.get_by_id(p.patient_id)
            doctor = await self.user_crud.get_by_id(p.doctor_id)

            return {
                "id": str(p.id),
                "appointment_id": p.appointment_id,
                "patient_id": p.patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Patient",
                "doctor_id": p.doctor_id,
                "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Doctor",
                "diagnosis": p.diagnosis,
                "medicines": p.medicines,
                "notes": p.notes,
                "pdf_url": p.pdf_url,
                "created_at": p.created_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error fetching prescription by appointment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching prescription.",
            )

    async def get_prescription_by_id(self, prescription_id: str, authorization: str) -> dict:
        try:
            logging.info(f"Fetching prescription by ID: {prescription_id}")
            payload = verify_token(authorization)
            caller_id = payload["id"]

            p = await self.prescription_crud.get_by_id(prescription_id)
            if not p:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prescription not found.",
                )

            # Strict authorization check
            if p.patient_id != caller_id and p.doctor_id != caller_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this prescription.",
                )

            patient = await self.user_crud.get_by_id(p.patient_id)
            doctor = await self.user_crud.get_by_id(p.doctor_id)

            return {
                "id": str(p.id),
                "appointment_id": p.appointment_id,
                "patient_id": p.patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Patient",
                "doctor_id": p.doctor_id,
                "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Doctor",
                "diagnosis": p.diagnosis,
                "medicines": p.medicines,
                "notes": p.notes,
                "pdf_url": p.pdf_url,
                "created_at": p.created_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error fetching prescription by ID: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching prescription.",
            )
