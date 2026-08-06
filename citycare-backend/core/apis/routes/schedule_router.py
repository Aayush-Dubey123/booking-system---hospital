from datetime import date

from fastapi import APIRouter, HTTPException, status

from core.controllers.schedule_controller import ScheduleController
from core.apis.schemas.responses.schedule_response import ScheduleResponse
from common.logger import logger

logging = logger(__name__)

schedule_router = APIRouter()


@schedule_router.get(
    "/v1/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ScheduleResponse,
)
async def get_schedule(appointment_date: date):
    try:
        logging.info("Calling /v1/schedule endpoint")

        result = await ScheduleController().get_schedule(appointment_date)

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
