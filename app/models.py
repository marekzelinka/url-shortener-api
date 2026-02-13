import re
from datetime import UTC, datetime
from enum import Enum
from functools import partial
from typing import Annotated, TypeVar

from beanie import Document, Indexed, PydanticObjectId, SortDirection
from pydantic import (
    AfterValidator,
    AnyUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)
from pydantic.generics import GenericModel
from slugify import slugify

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class Paginated[SchemaType](GenericModel):
    page: int
    per_page: int
    total: int
    results: list[SchemaType]


class PaginationParams(BaseModel):
    page: Annotated[int, Field(ge=1)] = 1
    per_page: Annotated[int, Field(ge=1, le=100)] = 10

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"

    def __int__(self) -> int:
        """Converts the enum to an integer to be used by MongoDB."""
        return 1 if self.value == "asc" else -1

    @property
    def direction(self) -> SortDirection:
        return SortDirection(int(self))


class SortingParams(BaseModel):
    sort: str = "created_at"
    order: SortOrder = SortOrder.ASC


ConstrainedUsername = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=64,
        pattern=re.compile(r"^[A-Za-z0-9-_.]+$"),
        to_lower=True,
        strip_whitespace=True,
    ),
]


class User(Document):
    class Settings:
        name = "users"
        use_state_management = True

    username: Annotated[ConstrainedUsername, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    password_hash: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: Annotated[
        datetime, Field(default_factory=partial(datetime.now, tz=UTC))
    ]


class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: EmailStr


class UserIn(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserPrivateUpdate(UserUpdate):
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime


class UserOutPrivate(UserBase):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    is_superuser: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


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
    slug: Annotated[str, Indexed(unique=True)]
    user_id: PydanticObjectId


class ShortUrlIn(BaseModel):
    url: AnyUrl
    slug: Annotated[str, Field(min_length=1, max_length=64), AfterValidator(slugify)]
    expiration_days: Annotated[float | None, Field(ge=0.0)] = None


class ShortUrlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ident: str
    origin: AnyUrl
    views: int
    created_at: datetime
    expires_at: datetime | None = None
    last_visit_at: datetime | None = None
    slug: str


class ShortUrlOutPrivate(ShortUrlOut):
    user_id: PydanticObjectId


__beanie_models__ = [User, ShortUrl]
