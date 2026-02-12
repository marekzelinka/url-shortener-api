import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import hash_password
from app.deps import CurrentActiveUserDep, CurrentUserDep
from app.models import (
    Paginated,
    PaginationParams,
    ShortUrl,
    ShortUrlPublic,
    SortingParams,
    User,
    UserCreate,
    UserPrivate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPrivate)
async def create_user(*, user: UserCreate) -> User:
    duplicate_username_user = await User.find(
        {"username": {"$regex": f"^{re.escape(user.username)}$", "$options": "i"}}
    ).first_or_none()
    if duplicate_username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    duplicate_email_user = await User.find(
        {"email": {"$regex": f"^{re.escape(user.email)}$", "$options": "i"}}
    ).first_or_none()
    if duplicate_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    db_user = User(
        **user.model_dump(exclude={"email", "password"}),
        email=user.email.lower(),
        password_hash=hash_password(user.password),
    )
    await db_user.insert()

    return db_user


@router.get("/me", response_model=UserPrivate)
async def read_current_user(*, current_user: CurrentUserDep) -> User:
    return current_user


@router.get("/me/urls", response_model=Paginated[ShortUrlPublic])
async def read_current_user_urls(
    *,
    current_user: CurrentActiveUserDep,
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[SortingParams, Depends()],
) -> Paginated[ShortUrl]:
    short_urls = (
        await ShortUrl.find(ShortUrl.user_id == current_user.id)
        .skip(pagination_params.skip)
        .limit(pagination_params.limit)
        .sort((sort_params.sort, sort_params.order.direction))
        .to_list()
    )

    return Paginated[ShortUrl](
        page=pagination_params.page,
        per_page=pagination_params.per_page,
        total=await ShortUrl.count(),
        results=short_urls,
    )
