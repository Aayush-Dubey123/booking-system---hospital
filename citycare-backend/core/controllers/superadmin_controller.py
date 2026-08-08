from fastapi import HTTPException, status

from core.cruds.hospital_crud import HospitalCRUD
from core.cruds.user_crud import UserCRUD
from common.auth_helpers import verify_token, require_role
from common.logger import logger

logging = logger(__name__)


class SuperadminController:
    def __init__(self) -> None:
        self.hospital_crud = HospitalCRUD()
        self.user_crud = UserCRUD()

    async def get_all_owners(self, authorization: str) -> list[dict]:
        """List all owners — superadmin only."""
        try:
            logging.info("Calling SuperadminController.get_all_owners")
            payload = verify_token(authorization)
            require_role(payload, "superadmin")

            owners = await self.user_crud.get_all_owners()
            result = []
            for o in owners:
                hospital_name = None
                if o.hospital_id:
                    hospital = await self.hospital_crud.get_by_id(o.hospital_id)
                    if hospital:
                        hospital_name = hospital.name

                result.append(
                    {
                        "id": str(o.id),
                        "first_name": o.first_name,
                        "last_name": o.last_name,
                        "email": o.email,
                        "hospital_id": o.hospital_id,
                        "hospital_name": hospital_name,
                    }
                )

            return result
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in SuperadminController.get_all_owners: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching owners.",
            )

    async def get_all_doctors(self, authorization: str) -> list[dict]:
        """List all doctors — superadmin only."""
        try:
            logging.info("Calling SuperadminController.get_all_doctors")
            payload = verify_token(authorization)
            require_role(payload, "superadmin")

            doctors = await self.user_crud.get_all_doctors()
            result = []
            for d in doctors:
                hospital_name = None
                if d.hospital_id:
                    hospital = await self.hospital_crud.get_by_id(d.hospital_id)
                    if hospital:
                        hospital_name = hospital.name

                result.append(
                    {
                        "id": str(d.id),
                        "first_name": d.first_name,
                        "last_name": d.last_name,
                        "email": d.email,
                        "hospital_id": d.hospital_id,
                        "hospital_name": hospital_name,
                    }
                )

            return result
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in SuperadminController.get_all_doctors: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching doctors.",
            )

    async def delete_user(self, user_id: str, authorization: str) -> dict:
        """Delete a user (owner or doctor) — superadmin only."""
        try:
            logging.info("Calling SuperadminController.delete_user")
            payload = verify_token(authorization)
            require_role(payload, "superadmin")

            user = await self.user_crud.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            if user.role == "superadmin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot delete a superadmin.",
                )

            deleted = await self.user_crud.delete_user(user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            logging.info(f"User {user_id} deleted successfully")
            return {"message": f"User {user_id} deleted successfully."}
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in SuperadminController.delete_user: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting user.",
            )
