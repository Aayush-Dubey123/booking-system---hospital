from fastapi import APIRouter, HTTPException, status

from core.controllers.user_controller import UserController
from core.apis.schemas.requests.user_request import UserSignUpRequest, UserLoginRequest
from core.apis.schemas.responses.user_response import UserResponse, UserLoginResponse
from common.logger import logger

logging = logger(__name__)

auth_router = APIRouter()


@auth_router.post(
    "/v1/users/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def user_signup(request: UserSignUpRequest):
    try:
        logging.info("Calling /v1/users/signup endpoint")
        data = request.model_dump()
        result = await UserController().register_user(data)
        return result
    except HTTPException as httperror:
        logging.error(f"Error in /v1/users/signup: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in /v1/users/signup: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@auth_router.post(
    "/v1/users/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
)
async def user_login(request: UserLoginRequest):
    try:
        logging.info("Calling /v1/users/login endpoint")

        data = request.model_dump()

        result = await UserController().login_user(data)

        return result

    except HTTPException as httperror:
        logging.error(f"Error in /v1/users/login: {httperror}")
        raise

    except Exception as error:
        logging.error(f"Error in /v1/users/login: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
