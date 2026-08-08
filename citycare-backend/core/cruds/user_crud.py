from bson import ObjectId
from odmantic import AIOEngine

from core.database.database import get_engine
from core.models.user_model import User
from common.logger import logger

logging = logger(__name__)


class UserCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def create_user(self, user: dict) -> User:
        try:
            logging.info("Creating a new user")
            return await self.engine.save(User(**user))
        except Exception as error:
            logging.error(f"Error creating user: {error}")
            raise

    async def get_by_email(self, email: str) -> User | None:
        try:
            logging.info(f"Finding user with email: {email}")
            return await self.engine.find_one(
                User,
                User.email == email,
            )
        except Exception as error:
            logging.error(f"Error finding user by email: {error}")
            raise

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            logging.info(f"Finding user with id: {user_id}")

            return await self.engine.find_one(
                User,
                User.id == ObjectId(user_id),
            )

        except Exception as error:
            logging.error(f"Error finding user by id: {error}")
            raise

    async def get_total_patients(self) -> int:
        try:
            logging.info("Fetching total patients")

            patients = await self.engine.find(
                User,
                User.role == "patient",
            )

            return len(patients)

        except Exception as error:
            logging.error(f"Error fetching total patients: {error}")
            raise

    async def get_doctors_by_hospital(self, hospital_id: str) -> list[User]:
        try:
            logging.info(f"Fetching doctors for hospital: {hospital_id}")
            return await self.engine.find(
                User,
                (User.role == "doctor") & (User.hospital_id == hospital_id),
            )
        except Exception as error:
            logging.error(f"Error fetching doctors by hospital: {error}")
            raise

    async def get_all_doctors(self) -> list[User]:
        try:
            logging.info("Fetching all doctors")
            return await self.engine.find(User, User.role == "doctor")
        except Exception as error:
            logging.error(f"Error fetching all doctors: {error}")
            raise

    async def get_all_owners(self) -> list[User]:
        try:
            logging.info("Fetching all owners")
            return await self.engine.find(User, User.role == "owner")
        except Exception as error:
            logging.error(f"Error fetching all owners: {error}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        try:
            logging.info(f"Deleting user: {user_id}")
            user = await self.get_by_id(user_id)
            if user:
                await self.engine.delete(user)
                return True
            return False
        except Exception as error:
            logging.error(f"Error deleting user: {error}")
            raise

    async def save_user(self, user: User) -> User:
        try:
            logging.info(f"Saving user: {user.id}")
            return await self.engine.save(user)
        except Exception as error:
            logging.error(f"Error saving user: {error}")
            raise
            raise