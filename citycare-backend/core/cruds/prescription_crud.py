from typing import Optional
from odmantic import AIOEngine, ObjectId
from core.database.database import get_engine
from core.models.prescription_model import Prescription
from common.logger import logger

logging = logger(__name__)


class PrescriptionCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def create_prescription(self, prescription_data: dict) -> Prescription:
        try:
            logging.info("Creating prescription")
            prescription = Prescription(**prescription_data)
            return await self.engine.save(prescription)
        except Exception as error:
            logging.error(f"Error creating prescription: {error}")
            raise

    async def get_by_id(self, prescription_id: str) -> Optional[Prescription]:
        try:
            logging.info(f"Fetching prescription by ID: {prescription_id}")
            try:
                oid = ObjectId(prescription_id)
            except Exception:
                return None
            return await self.engine.find_one(Prescription, Prescription.id == oid)
        except Exception as error:
            logging.error(f"Error fetching prescription by ID: {error}")
            raise

    async def get_by_appointment_id(self, appointment_id: str) -> Optional[Prescription]:
        try:
            logging.info(f"Fetching prescription for appointment: {appointment_id}")
            return await self.engine.find_one(
                Prescription, Prescription.appointment_id == appointment_id
            )
        except Exception as error:
            logging.error(f"Error fetching prescription by appointment ID: {error}")
            raise

    async def get_by_patient_id(self, patient_id: str) -> list[Prescription]:
        try:
            logging.info(f"Fetching prescriptions for patient: {patient_id}")
            return await self.engine.find(
                Prescription, Prescription.patient_id == patient_id
            )
        except Exception as error:
            logging.error(f"Error fetching patient prescriptions: {error}")
            raise

    async def get_by_doctor_id(self, doctor_id: str) -> list[Prescription]:
        try:
            logging.info(f"Fetching prescriptions for doctor: {doctor_id}")
            return await self.engine.find(
                Prescription, Prescription.doctor_id == doctor_id
            )
        except Exception as error:
            logging.error(f"Error fetching doctor prescriptions: {error}")
            raise
