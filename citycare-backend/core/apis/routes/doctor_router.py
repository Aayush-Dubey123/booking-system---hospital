from datetime import date

from fastapi import APIRouter, Header, HTTPException, Query, status

from common.logger import logger
from core.controllers.doctor_controller import DoctorController
from core.apis.schemas.responses.doctor_response import (
    DoctorDashboardResponse,
    DoctorScheduleResponse,
)

logging = logger(__name__)

doctor_router = APIRouter()


@doctor_router.get(
    "/v1/doctor/dashboard",
    response_model=DoctorDashboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_doctor_dashboard(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/doctor/dashboard endpoint")

        return await DoctorController().get_dashboard(
            authorization,
        )

    except HTTPException:
        raise

    except Exception as error:
        logging.error(
            f"Error in /v1/doctor/dashboard: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@doctor_router.get(
    "/v1/doctor/schedule",
    response_model=list[DoctorScheduleResponse],
    status_code=status.HTTP_200_OK,
)
async def get_doctor_schedule(
    appointment_date: date = Query(...),
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/doctor/schedule endpoint")

        return await DoctorController().get_schedule(
            appointment_date,
            authorization,
        )

    except HTTPException:
        raise

    except Exception as error:
        logging.error(
            f"Error in /v1/doctor/schedule: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )