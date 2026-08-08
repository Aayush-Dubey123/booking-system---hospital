from fastapi import APIRouter, Header, HTTPException, status

from core.controllers.superadmin_controller import SuperadminController
from core.apis.schemas.responses.hospital_response import (
    OwnerResponse,
    DoctorOfHospitalResponse,
)
from common.logger import logger

logging = logger(__name__)

superadmin_router = APIRouter()


@superadmin_router.get(
    "/v1/admin/owners",
    status_code=status.HTTP_200_OK,
    response_model=list[OwnerResponse],
)
async def get_all_owners(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/admin/owners endpoint")
        return await SuperadminController().get_all_owners(authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/admin/owners: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@superadmin_router.get(
    "/v1/admin/doctors",
    status_code=status.HTTP_200_OK,
)
async def get_all_doctors(
    authorization: str = Header(...),
):
    try:
        logging.info("Calling /v1/admin/doctors endpoint")
        return await SuperadminController().get_all_doctors(authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in /v1/admin/doctors: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@superadmin_router.delete(
    "/v1/admin/users/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: str,
    authorization: str = Header(...),
):
    try:
        logging.info(f"Calling DELETE /v1/admin/users/{user_id} endpoint")
        return await SuperadminController().delete_user(user_id, authorization)
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Error in DELETE /v1/admin/users/{{id}}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
