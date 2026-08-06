from fastapi import APIRouter, HTTPException, status

from core.controllers.dashboard_controller import DashboardController
from core.apis.schemas.responses.dashboard_response import DashboardResponse
from common.logger import logger

logging = logger(__name__)

dashboard_router = APIRouter()


@dashboard_router.get(
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
