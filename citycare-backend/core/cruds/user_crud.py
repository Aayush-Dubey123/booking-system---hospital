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
            return await self.engine.find_one(User, User.email == email)
        except Exception as error:
            logging.error(f"Error finding user by email: {error}")
            raise