from bson import ObjectId
from odmantic import AIOEngine

from core.database.database import get_engine
from core.models.hospital_model import Hospital
from common.logger import logger

logging = logger(__name__)


class HospitalCRUD:
    def __init__(self) -> None:
        self.engine: AIOEngine = get_engine()

    async def create_hospital(self, hospital: dict) -> Hospital:
        try:
            logging.info("Creating a new hospital")
            return await self.engine.save(Hospital(**hospital))
        except Exception as error:
            logging.error(f"Error creating hospital: {error}")
            raise

    async def get_all(self) -> list[Hospital]:
        try:
            logging.info("Fetching all hospitals")
            return await self.engine.find(Hospital)
        except Exception as error:
            logging.error(f"Error fetching hospitals: {error}")
            raise

    async def get_by_id(self, hospital_id: str) -> Hospital | None:
        try:
            logging.info(f"Finding hospital with id: {hospital_id}")
            return await self.engine.find_one(
                Hospital,
                Hospital.id == ObjectId(hospital_id),
            )
        except Exception as error:
            logging.error(f"Error finding hospital by id: {error}")
            raise

    async def get_by_owner_id(self, owner_id: str) -> Hospital | None:
        try:
            logging.info(f"Finding hospital for owner: {owner_id}")
            return await self.engine.find_one(
                Hospital,
                Hospital.owner_id == owner_id,
            )
        except Exception as error:
            logging.error(f"Error finding hospital by owner: {error}")
            raise

    async def delete_hospital(self, hospital_id: str) -> bool:
        try:
            logging.info(f"Deleting hospital: {hospital_id}")
            hospital = await self.get_by_id(hospital_id)
            if hospital:
                await self.engine.delete(hospital)
                return True
            return False
        except Exception as error:
            logging.error(f"Error deleting hospital: {error}")
            raise
