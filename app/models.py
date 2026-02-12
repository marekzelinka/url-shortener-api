from datetime import UTC, datetime
from functools import partial
from typing import Annotated

from beanie import Document, Indexed
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, field_validator


class ShortUrlCreate(BaseModel):
    url: AnyUrl
    slug: Annotated[str | None, Field(min_length=1, max_length=64)] = None
    expiration_days: Annotated[float | None, Field(ge=0.0)] = None

    @field_validator("slug", mode="after")
    @classmethod
    def normalize_slug(cls, slug: str | None) -> str | None:
        """Transforms existing slug by lowercasing and replacing spaces with dashes."""
        if slug is not None:
            slug = slug.strip().lower().replace(" ", "-")
        return slug


class ShortUrl(Document):
    class Settings:
        name = "urls"
        use_state_management = True

    ident: Annotated[str, Indexed(unique=True)]
    origin: str
    views: int = 0
    created_at: Annotated[
        datetime, Field(default_factory=partial(datetime.now, tz=UTC))
    ]
    expires_at: Annotated[datetime | None, Indexed(expireAfterSeconds=0)] = None
    last_visit_at: datetime | None = None
    slug: Annotated[str | None, Indexed(unique=True)] = None


class ShortUrlPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ident: str
    origin: AnyUrl
    views: int
    created_at: datetime
    expire_at: datetime | None = None
    last_visit_at: datetime | None = None
    slug: str | None = None


__beanie_models__ = [ShortUrl]
