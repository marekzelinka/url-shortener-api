from typing import Annotated

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    SecretStr,
    UrlConstraints,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: str | list[str] | None) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    if isinstance(v, list | str):
        return v

    raise ValueError(v)


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

    # CORS
    cors_origins: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.cors_origins]

    # Auth
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Superuser
    first_superuser: str
    first_superuser_email: EmailStr
    first_superuser_password: SecretStr

    # URLs
    url_ident_length: int = 7


config = Settings.model_validate({})
