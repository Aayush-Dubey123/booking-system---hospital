from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from common.logger import logger
from core.controllers.prescription_controller import PrescriptionController

logging = logger(__name__)

prescription_router = APIRouter()


class CreatePrescriptionRequest(BaseModel):
    appointment_id: str
    diagnosis: str
    medicines: str
    notes: Optional[str] = ""


@prescription_router.post(
    "/v1/prescriptions",
    status_code=status.HTTP_201_CREATED,
)
async def create_prescription(
    request: CreatePrescriptionRequest,
    authorization: str = Header(...),
):
    try:
        logging.info("Calling POST /v1/prescriptions endpoint")
        data = request.model_dump()
        return await PrescriptionController().create_prescription(data, authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in POST /v1/prescriptions: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@prescription_router.get(
    "/v1/prescriptions/my",
    status_code=status.HTTP_200_OK,
)
async def get_my_prescriptions(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling GET /v1/prescriptions/my endpoint")
        return await PrescriptionController().get_my_prescriptions(authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in GET /v1/prescriptions/my: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@prescription_router.get(
    "/v1/prescriptions/appointment/{appointment_id}",
    status_code=status.HTTP_200_OK,
)
async def get_prescription_by_appointment(
    appointment_id: str,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling GET /v1/prescriptions/appointment/{appointment_id} endpoint")
        return await PrescriptionController().get_prescription_by_appointment(
            appointment_id, authorization
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in GET /v1/prescriptions/appointment/{appointment_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@prescription_router.get(
    "/v1/prescriptions/{prescription_id}",
    status_code=status.HTTP_200_OK,
)
async def get_prescription_by_id(
    prescription_id: str,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling GET /v1/prescriptions/{prescription_id} endpoint")
        return await PrescriptionController().get_prescription_by_id(
            prescription_id, authorization
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in GET /v1/prescriptions/{prescription_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
