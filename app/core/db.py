from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import config
from app.models import __beanie_models__


async def init_db() -> None:
    client = AsyncMongoClient(str(config.mongo_uri), tz_aware=True)
    await init_beanie(
        database=client[config.mongo_db_name], document_models=__beanie_models__
    )
