from fastapi import APIRouter, HTTPException, Header, status

from core.controllers.my_appointments_controller import MyAppointmentsController
from core.apis.schemas.responses.my_appointments_response import MyAppointmentResponse
from common.logger import logger

logging = logger(__name__)

my_appointments_router = APIRouter()


@my_appointments_router.get(
    "/v1/appointments/my",
    status_code=status.HTTP_200_OK,
    response_model=list[MyAppointmentResponse],
)
async def get_my_appointments(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/appointments/my endpoint")

        result = await MyAppointmentsController().get_my_appointments(authorization)

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
