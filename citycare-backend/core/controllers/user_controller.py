from fastapi import HTTPException, status

from core.cruds.user_crud import UserCRUD
from common.auth import encrypt_password, verify_password, signJWT
from common.logger import logger

logging = logger(__name__)


class UserController:
    def __init__(self) -> None:
        self.user_crud = UserCRUD()

    async def register_user(self, request: dict) -> dict:
        try:
            logging.info("Calling UserController.register_user")

            existing_user = await self.user_crud.get_by_email(request["email"])

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered.",
                )

            request["password"] = encrypt_password(request["password"])
            request["role"] = "patient"

            user = await self.user_crud.create_user(request)

            logging.info("User registered successfully")

            return {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(f"Error in UserController.register_user: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration.",
            )

    async def login_user(self, request: dict) -> dict:
        try:
            logging.info("Calling UserController.login_user")

            user = await self.user_crud.get_by_email(request["email"])

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

            if not verify_password(request["password"], user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

            access_token = signJWT(role=user.role, id=str(user.id))

            logging.info("User logged in successfully")

            return {
                "access_token": access_token,
                "role": user.role,
                "hospital_id": user.hospital_id,
            }

        except HTTPException:
            raise

        except Exception as error:
            logging.error(f"Error in UserController.login_user: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login.",
            )