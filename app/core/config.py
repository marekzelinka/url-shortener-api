from typing import Annotated

from pydantic import UrlConstraints
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    mongo_uri: Annotated[
        MultiHostUrl,
        UrlConstraints(allowed_schemes=["mongodb", "mongodb+srv"]),
    ]
    mongo_db_name: str


config = Settings.model_validate({})
