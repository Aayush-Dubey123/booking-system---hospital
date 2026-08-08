from fastapi import HTTPException, status

from core.cruds.hospital_crud import HospitalCRUD
from core.cruds.user_crud import UserCRUD
from core.cruds.appointment_crud import AppointmentCRUD
from common.auth import encrypt_password
from common.auth_helpers import verify_token, require_role
from common.logger import logger

logging = logger(__name__)


class HospitalController:
    def __init__(self) -> None:
        self.hospital_crud = HospitalCRUD()
        self.user_crud = UserCRUD()
        self.appointment_crud = AppointmentCRUD()

    async def list_hospitals(self) -> list[dict]:
        """List all hospitals — accessible to any authenticated user."""
        try:
            logging.info("Calling HospitalController.list_hospitals")
            hospitals = await self.hospital_crud.get_all()
            return [
                {
                    "id": str(h.id),
                    "name": h.name,
                    "address": h.address,
                    "phone": h.phone,
                }
                for h in hospitals
            ]
        except Exception as error:
            logging.error(f"Error in HospitalController.list_hospitals: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching hospitals.",
            )

    async def get_hospital(self, hospital_id: str) -> dict:
        """Get a single hospital by ID."""
        try:
            logging.info("Calling HospitalController.get_hospital")
            hospital = await self.hospital_crud.get_by_id(hospital_id)
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hospital not found.",
                )
            return {
                "id": str(hospital.id),
                "name": hospital.name,
                "address": hospital.address,
                "phone": hospital.phone,
                "owner_id": hospital.owner_id,
                "created_at": hospital.created_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in HospitalController.get_hospital: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching hospital.",
            )

    async def create_hospital(
        self, request: dict, authorization: str
    ) -> dict:
        """Create a hospital and its owner — superadmin only."""
        try:
            logging.info("Calling HospitalController.create_hospital")
            payload = verify_token(authorization)
            require_role(payload, "superadmin")

            # Check if owner email is already taken
            existing_user = await self.user_crud.get_by_email(request["owner_email"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Owner email already registered.",
                )

            # 1. Create the hospital first without owner_id
            hospital_data = {
                "name": request["name"],
                "address": request["address"],
                "phone": request["phone"]
            }
            hospital = await self.hospital_crud.create_hospital(hospital_data)
            
            # 2. Create the owner linked to the hospital
            owner_data = {
                "first_name": request["owner_first_name"],
                "last_name": request["owner_last_name"],
                "email": request["owner_email"],
                "password": encrypt_password(request["owner_password"]),
                "role": "owner",
                "hospital_id": str(hospital.id)
            }
            owner = await self.user_crud.create_user(owner_data)

            # 3. Update hospital with owner_id
            hospital.owner_id = str(owner.id)
            await self.hospital_crud.engine.save(hospital)

            logging.info("Hospital and owner created successfully")

            return {
                "id": str(hospital.id),
                "name": hospital.name,
                "address": hospital.address,
                "phone": hospital.phone,
                "owner_id": hospital.owner_id,
                "created_at": hospital.created_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in HospitalController.create_hospital: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating hospital.",
            )

    async def get_hospital_doctors(
        self, hospital_id: str, authorization: str
    ) -> list[dict]:
        """Get doctors of a hospital — owner (own hospital) or superadmin."""
        try:
            logging.info("Calling HospitalController.get_hospital_doctors")
            payload = verify_token(authorization)
            require_role(payload, "owner", "superadmin")

            # Owner can only see their own hospital's doctors
            if payload["role"] == "owner":
                owner = await self.user_crud.get_by_id(payload["id"])
                if not owner or owner.hospital_id != hospital_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied. Not your hospital.",
                    )

            doctors = await self.user_crud.get_doctors_by_hospital(hospital_id)
            return [
                {
                    "id": str(d.id),
                    "first_name": d.first_name,
                    "last_name": d.last_name,
                    "email": d.email,
                    "hospital_id": d.hospital_id,
                }
                for d in doctors
            ]
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in HospitalController.get_hospital_doctors: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching doctors.",
            )

    async def add_doctor_to_hospital(
        self, hospital_id: str, request: dict, authorization: str
    ) -> dict:
        """Add a doctor to a hospital — owner (own hospital) or superadmin."""
        try:
            logging.info("Calling HospitalController.add_doctor_to_hospital")
            payload = verify_token(authorization)
            require_role(payload, "owner", "superadmin")

            # Owner can only add to their own hospital
            if payload["role"] == "owner":
                owner = await self.user_crud.get_by_id(payload["id"])
                if not owner or owner.hospital_id != hospital_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied. Not your hospital.",
                    )

            # Verify hospital exists
            hospital = await self.hospital_crud.get_by_id(hospital_id)
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hospital not found.",
                )

            # Check if email already taken
            existing = await self.user_crud.get_by_email(request["email"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered.",
                )

            doctor_data = {
                "first_name": request["first_name"],
                "last_name": request["last_name"],
                "email": request["email"],
                "password": encrypt_password(request["password"]),
                "role": "doctor",
                "hospital_id": hospital_id,
            }

            doctor = await self.user_crud.create_user(doctor_data)
            logging.info("Doctor added to hospital successfully")

            return {
                "id": str(doctor.id),
                "first_name": doctor.first_name,
                "last_name": doctor.last_name,
                "email": doctor.email,
                "hospital_id": doctor.hospital_id,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(
                f"Error in HospitalController.add_doctor_to_hospital: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while adding doctor.",
            )

    async def get_hospital_appointments(
        self, hospital_id: str, authorization: str
    ) -> list[dict]:
        """Get appointments of a hospital — owner or doctor (own hospital)."""
        try:
            logging.info("Calling HospitalController.get_hospital_appointments")
            payload = verify_token(authorization)
            require_role(payload, "owner", "doctor", "superadmin")

            user = await self.user_crud.get_by_id(payload["id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found.",
                )

            # Owner/doctor can only see their own hospital
            if payload["role"] in ("owner", "doctor"):
                if user.hospital_id != hospital_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied. Not your hospital.",
                    )

            appointments = await self.appointment_crud.get_appointments_by_hospital(
                hospital_id
            )

            response = []
            for appt in appointments:
                patient = await self.user_crud.get_by_id(appt.patient_id)
                patient_name = (
                    f"{patient.first_name} {patient.last_name}"
                    if patient
                    else "Unknown Patient"
                )

                doctor_name = None
                if appt.doctor_id:
                    doctor = await self.user_crud.get_by_id(appt.doctor_id)
                    if doctor:
                        doctor_name = f"{doctor.first_name} {doctor.last_name}"

                response.append(
                    {
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
                    }
                )

            return response
        except HTTPException:
            raise
        except Exception as error:
            logging.error(
                f"Error in HospitalController.get_hospital_appointments: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching appointments.",
            )
