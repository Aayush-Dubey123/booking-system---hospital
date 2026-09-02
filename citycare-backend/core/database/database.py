import logging
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()
import certifi
from motor import core, motor_asyncio
from odmantic import AIOEngine
from pymongo.driver_info import DriverInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRIVER_INFO = DriverInfo(name="citycare-backend", version="1.0.0")

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME") or os.getenv("MONGODB_NAME") or "citycare"


class _MongoClientSingleton:
    mongo_client: Optional[motor_asyncio.AsyncIOMotorClient] = None
    engine: Optional[AIOEngine] = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(_MongoClientSingleton, cls).__new__(cls)

            client_kwargs = {
                "driver": DRIVER_INFO,
            }
            if "mongodb+srv://" in MONGODB_URL or "ssl=true" in MONGODB_URL.lower() or "tls=true" in MONGODB_URL.lower():
                client_kwargs["tlsCAFile"] = certifi.where()

            cls.instance.mongo_client = motor_asyncio.AsyncIOMotorClient(
                MONGODB_URL,
                **client_kwargs,
            )

            cls.instance.engine = AIOEngine(
                client=cls.instance.mongo_client,
                database=DATABASE_NAME,
            )

            logger.info(f"MongoDB initialized | Database: {DATABASE_NAME}")

        return cls.instance


def MongoDatabase() -> core.AgnosticDatabase:
    return _MongoClientSingleton().mongo_client[DATABASE_NAME]


def get_engine() -> AIOEngine:
    return _MongoClientSingleton().engine


async def ping() -> None:
    await MongoDatabase().command("ping")
    logger.info("MongoDB ping successful")


async def connect_to_mongo() -> None:
    logger.info("Connecting to MongoDB...")
    _MongoClientSingleton()
    await ping()
    logger.info("MongoDB connection established")


async def close_mongo_connection() -> None:
    singleton = _MongoClientSingleton()

    if singleton.mongo_client:
        singleton.mongo_client.close()
        logger.info("MongoDB connection closed")