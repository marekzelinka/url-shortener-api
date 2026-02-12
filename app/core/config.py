from typing import Annotated

from pydantic import SecretStr, UrlConstraints
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # MongoDB
    mongo_uri: Annotated[
        MultiHostUrl,
        UrlConstraints(allowed_schemes=["mongodb", "mongodb+srv"]),
    ]
    mongo_db_name: str

    # Auth
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # URLs
    url_ident_length: int = 7


config = Settings.model_validate({})
