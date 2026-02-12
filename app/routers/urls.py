from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import config
from app.models import (
    Paginated,
    PaginationParams,
    ShortUrl,
    ShortUrlCreate,
    ShortUrlPublic,
    SortingParams,
)
from app.utils import generate_url_ident

router = APIRouter(tags=["urls"])


@router.post(
    "/shorten", status_code=status.HTTP_201_CREATED, response_model=ShortUrlPublic
)
async def create_short_url(*, short_url: ShortUrlCreate) -> ShortUrl:
    if short_url.slug is not None:
        existing_short_url = await ShortUrl.find(
            ShortUrl.slug == short_url.slug
        ).first_or_none()
        if existing_short_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The URL associated with this slug already exists",
            )

    origin = str(short_url.url)
    expires_at = (
        (datetime.now(tz=UTC) + timedelta(days=short_url.expiration_days))
        if short_url.expiration_days
        else None
    )

    db_short_url = ShortUrl(
        **short_url.model_dump(
            exclude={"url", "expiration_days"},
        ),
        ident=generate_url_ident(origin, config.url_ident_length),
        origin=origin,
        expires_at=expires_at,
    )
    await db_short_url.insert()

    return db_short_url


@router.get("/shorten", response_model=Paginated[ShortUrlPublic])
async def read_urls(
    *,
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[SortingParams, Depends()],
) -> Paginated[ShortUrl]:
    short_urls = (
        await ShortUrl.find()
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
