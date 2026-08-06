from fastapi import APIRouter, HTTPException, Header, status

from core.controllers.appointment_controller import AppointmentController
from core.apis.schemas.requests.appointment_request import AppointmentRequest
from core.apis.schemas.responses.appointment_response import AppointmentResponse
from common.logger import logger

logging = logger(__name__)

appointment_router = APIRouter()


@appointment_router.post(
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