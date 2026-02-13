from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from app.core.config import config
from app.deps import (
    CurrentActiveSuperUserDep,
    CurrentActiveUserDep,
    PaginationParamsDep,
    SortParamsDep,
)
from app.models import (
    Paginated,
    ShortUrl,
    ShortUrlIn,
    ShortUrlOut,
    ShortUrlOutPrivate,
)
from app.utils import generate_url_ident

router = APIRouter(tags=["urls"])


@router.post(
    "/shorten", status_code=status.HTTP_201_CREATED, response_model=ShortUrlOut
)
async def create_short_url(
    *, user: CurrentActiveUserDep, short_url_in: ShortUrlIn
) -> ShortUrl:
    existing_short_url = await ShortUrl.find(
        ShortUrl.slug == short_url_in.slug
    ).first_or_none()
    if existing_short_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL associated with this slug already exists",
        )

    origin = str(short_url_in.url)
    expires_at = (
        (datetime.now(tz=UTC) + timedelta(days=short_url_in.expiration_days))
        if short_url_in.expiration_days
        else None
    )

    short_url = ShortUrl(
        **short_url_in.model_dump(
            exclude={"url", "expiration_days"},
        ),
        ident=generate_url_ident(origin, config.url_ident_length),
        origin=origin,
        expires_at=expires_at,
        user_id=user.id,
    )
    await short_url.insert()

    return short_url


@router.get("/urls", tags=["admin"], response_model=Paginated[ShortUrlOutPrivate])
async def read_short_urls(
    *,
    _superuser: CurrentActiveSuperUserDep,
    pagination_params: PaginationParamsDep,
    sort_params: SortParamsDep,
) -> Paginated:
    short_urls_query = ShortUrl.find()

    short_urls = (
        await short_urls_query.skip(pagination_params.skip)
        .limit(pagination_params.limit)
        .sort((sort_params.sort, sort_params.order.direction))
        .to_list()
    )
    total_count = await short_urls_query.count()

    return Paginated(
        page=pagination_params.page,
        per_page=pagination_params.per_page,
        total=total_count,
        results=short_urls,
    )


@router.get("/urls/{ident}", tags=["admin"], response_model=ShortUrlOutPrivate)
async def read_short_url(
    *, _superuser: CurrentActiveSuperUserDep, ident: str
) -> ShortUrl:
    short_url = await ShortUrl.find(ShortUrl.ident == ident).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    return short_url


@router.patch("/urls/{ident}/refresh", response_model=ShortUrlOut)
async def refresh_short_url(*, user: CurrentActiveUserDep, ident: str) -> ShortUrl:
    short_url = await ShortUrl.find(
        ShortUrl.ident == ident, ShortUrl.user_id == user.id
    ).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    if short_url.expires_at:
        previous_expires_at = short_url.expires_at - short_url.created_at
        short_url.expires_at = datetime.now(tz=UTC) + previous_expires_at

        await short_url.save_changes()

    return short_url


@router.delete("/urls/{ident}", tags=["admin"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    *, _superuser: CurrentActiveSuperUserDep, ident: str
) -> None:
    short_url = await ShortUrl.find(ShortUrl.ident == ident).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    await short_url.delete()
