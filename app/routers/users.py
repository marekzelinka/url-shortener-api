import re

from beanie import SortDirection
from fastapi import APIRouter, HTTPException, status

from app.core.security import hash_password
from app.deps import (
    CurrentActiveSuperUserDep,
    CurrentActiveUserDep,
    PaginationParamsDep,
    SortParamsDep,
)
from app.models import (
    Paginated,
    ShortUrl,
    ShortUrlOut,
    User,
    UserIn,
    UserOut,
    UserOutPrivate,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(*, user_in: UserIn) -> User:
    duplicate_username_user = await User.find(
        {"username": {"$regex": f"^{re.escape(user_in.username)}$", "$options": "i"}}
    ).first_or_none()
    if duplicate_username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    duplicate_email_user = await User.find(
        {"email": {"$regex": f"^{re.escape(user_in.email)}$", "$options": "i"}}
    ).first_or_none()
    if duplicate_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    user = User(
        **user_in.model_dump(exclude={"email", "password"}),
        email=user_in.email.lower(),
        password_hash=hash_password(user_in.password),
    )
    await user.insert()

    return user


@router.get("/", tags=["admin"], response_model=Paginated[UserOutPrivate])
async def read_users(
    *,
    _superuser: CurrentActiveSuperUserDep,
    pagination_params: PaginationParamsDep,
    sort_params: SortParamsDep,
) -> Paginated[User]:
    users_query = User.find()

    total_count = await users_query.count()
    short_urls = (
        await users_query.skip(pagination_params.skip)
        .limit(pagination_params.limit)
        .sort((sort_params.sort, sort_params.order.direction))
        .to_list()
    )

    return Paginated(
        page=pagination_params.page,
        per_page=pagination_params.per_page,
        total=total_count,
        results=short_urls,
    )


@router.get("/me", response_model=UserOut)
async def read_current_user(*, user: CurrentActiveUserDep) -> User:
    return user


@router.get("/me/urls", response_model=Paginated[ShortUrlOut])
async def read_current_user_short_urls(
    *,
    user: CurrentActiveUserDep,
    pagination_params: PaginationParamsDep,
    sort_params: SortParamsDep,
) -> Paginated:
    short_urls_query = ShortUrl.find(ShortUrl.user_id == user.id)

    total_count = await short_urls_query.count()
    short_urls = (
        await short_urls_query.skip(pagination_params.skip)
        .limit(pagination_params.limit)
        .sort((sort_params.sort, sort_params.order.direction))
        .to_list()
    )

    return Paginated(
        page=pagination_params.page,
        per_page=pagination_params.per_page,
        total=total_count,
        results=short_urls,
    )


@router.get("/me/most-visited", response_model=Paginated[ShortUrlOut])
async def read_current_user_most_visited_short_urls(
    *, user: CurrentActiveUserDep, pagination_params: PaginationParamsDep
) -> Paginated:
    most_visited_short_urls_query = ShortUrl.find(ShortUrl.user_id == user.id)

    total_count = await most_visited_short_urls_query.count()
    most_visited_short_urls = (
        await most_visited_short_urls_query.skip(pagination_params.skip)
        .limit(pagination_params.limit)
        .sort(("views", SortDirection.DESCENDING))
        .to_list()
    )

    return Paginated(
        page=pagination_params.page,
        per_page=pagination_params.per_page,
        total=total_count,
        results=most_visited_short_urls,
    )


@router.patch("/me", response_model=UserOut)
async def update_current_user(
    *, user: CurrentActiveUserDep, updates: UserUpdate
) -> User:
    if updates.username is not None:
        duplicate_username_user = await User.find(
            {
                "username": {
                    "$regex": f"^{re.escape(updates.username)}$",
                    "$options": "i",
                }
            }
        ).first_or_none()
        if duplicate_username_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        user.username = updates.username

    if updates.email is not None:
        duplicate_email_user = await User.find(
            {"email": {"$regex": f"^{re.escape(updates.email)}$", "$options": "i"}}
        ).first_or_none()
        if duplicate_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

        user.email = updates.email.lower()

    if updates.password is not None:
        user.password_hash = hash_password(updates.password)

    await user.save_changes()

    return user
