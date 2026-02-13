from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import config
from app.core.security import hash_password
from app.models import User, __beanie_models__


async def init_db() -> None:
    client = AsyncMongoClient(str(config.mongo_uri), tz_aware=True)
    await init_beanie(
        database=client[config.mongo_db_name], document_models=__beanie_models__
    )

    superuser = await User.find(User.username == config.first_superuser).first_or_none()
    if not superuser:
        await User(
            username=config.first_superuser,
            email=config.first_superuser_email.lower(),
            password_hash=hash_password(
                config.first_superuser_password.get_secret_value()
            ),
            is_superuser=True,
        ).insert()
