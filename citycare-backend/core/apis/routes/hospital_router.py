from fastapi import APIRouter, Header, HTTPException, status

from core.controllers.hospital_controller import HospitalController
from core.apis.schemas.requests.hospital_request import (
    HospitalCreateRequest,
    AddDoctorRequest,
)
from core.apis.schemas.responses.hospital_response import (
    HospitalResponse,
    HospitalListResponse,
    DoctorOfHospitalResponse,
    HospitalAppointmentResponse,
)
from common.logger import logger

logging = logger(__name__)

hospital_router = APIRouter()


@hospital_router.get(
    "/v1/hospitals",
    status_code=status.HTTP_200_OK,
    response_model=list[HospitalListResponse],
)
async def list_hospitals():
    try:
        logging.info("Calling /v1/hospitals endpoint")
        return await HospitalController().list_hospitals()
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/hospitals: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@hospital_router.get(
    "/v1/hospitals/{hospital_id}",
    status_code=status.HTTP_200_OK,
    response_model=HospitalResponse,
)
async def get_hospital(hospital_id: str):
    try:
        logging.info(f"Calling /v1/hospitals/{hospital_id} endpoint")
        return await HospitalController().get_hospital(hospital_id)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/hospitals/{{id}}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@hospital_router.post(
    "/v1/hospitals",
    status_code=status.HTTP_201_CREATED,
    response_model=HospitalResponse,
)
async def create_hospital(
    request: HospitalCreateRequest,
    authorization: str = Header(...),
):
    try:
        logging.info("Calling POST /v1/hospitals endpoint")
        data = request.model_dump()
        return await HospitalController().create_hospital(data, authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in POST /v1/hospitals: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@hospital_router.get(
    "/v1/hospitals/{hospital_id}/doctors",
    status_code=status.HTTP_200_OK,
    response_model=list[DoctorOfHospitalResponse],
)
async def get_hospital_doctors(
    hospital_id: str,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling /v1/hospitals/{hospital_id}/doctors endpoint")
        return await HospitalController().get_hospital_doctors(
            hospital_id, authorization
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/hospitals/{{id}}/doctors: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@hospital_router.post(
    "/v1/hospitals/{hospital_id}/doctors",
    status_code=status.HTTP_201_CREATED,
    response_model=DoctorOfHospitalResponse,
)
async def add_doctor_to_hospital(
    hospital_id: str,
    request: AddDoctorRequest,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling POST /v1/hospitals/{hospital_id}/doctors endpoint")
        data = request.model_dump()
        return await HospitalController().add_doctor_to_hospital(
            hospital_id, data, authorization
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in POST /v1/hospitals/{{id}}/doctors: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@hospital_router.get(
    "/v1/hospitals/{hospital_id}/appointments",
    status_code=status.HTTP_200_OK,
    response_model=list[HospitalAppointmentResponse],
)
async def get_hospital_appointments(
    hospital_id: str,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling /v1/hospitals/{hospital_id}/appointments endpoint")
        return await HospitalController().get_hospital_appointments(
            hospital_id, authorization
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/hospitals/{{id}}/appointments: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
