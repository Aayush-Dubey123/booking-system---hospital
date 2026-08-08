from datetime import date
from fastapi import APIRouter, HTTPException, Header, status

from core.controllers.appointment_controller import AppointmentController
from core.controllers.dashboard_controller import DashboardController

from core.apis.schemas.requests.appointment_request import AppointmentRequest
from core.apis.schemas.responses.user_response import (
    AppointmentResponse,
    MyAppointmentResponse,
    ScheduleResponse,
    DashboardResponse,
)
from common.logger import logger

logging = logger(__name__)

user_router = APIRouter()


@user_router.post(
    "/v1/appointments/book",
    status_code=status.HTTP_201_CREATED,
    response_model=AppointmentResponse,
)
async def book_appointment(
    request: AppointmentRequest,
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/appointments/book endpoint")

        data = request.model_dump()

        result = await AppointmentController().book_appointment(
            data,
            authorization,
        )

        return result

    except HTTPException as httperror:
        logging.error(f"Error in /v1/appointments/book: {httperror}")
        raise

    except Exception as error:
        logging.error(f"Error in /v1/appointments/book: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@user_router.get(
    "/v1/appointments/my",
    status_code=status.HTTP_200_OK,
    response_model=list[MyAppointmentResponse],
)
async def get_my_appointments(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/appointments/my endpoint")

        result = await AppointmentController().get_my_appointments(authorization)

        return result

    except HTTPException as httperror:
        logging.error(f"Error in /v1/appointments/my: {httperror}")
        raise

    except Exception as error:
        logging.error(f"Error in /v1/appointments/my: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@user_router.get(
    "/v1/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ScheduleResponse,
)
async def get_schedule(appointment_date: date):
    try:
        logging.info("Calling /v1/schedule endpoint")

        result = await AppointmentController().get_schedule(appointment_date)

        return result

    except HTTPException as httperror:
        logging.error(f"Error in /v1/schedule: {httperror}")
        raise

    except Exception as error:
        logging.error(f"Error in /v1/schedule: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@user_router.get(
    "/v1/dashboard",
    status_code=status.HTTP_200_OK,
    response_model=DashboardResponse,
)
async def get_dashboard():
    try:
        logging.info("Calling /v1/dashboard endpoint")

        result = await DashboardController().get_dashboard()

        return result

    except HTTPException as httperror:
        logging.error(f"Error in /v1/dashboard: {httperror}")
        raise

    except Exception as error:
        logging.error(f"Error in /v1/dashboard: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
