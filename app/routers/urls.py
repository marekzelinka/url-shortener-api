from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import config
from app.deps import CurrentActiveUserDep
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
async def create_short_url(
    *, current_user: CurrentActiveUserDep, short_url: ShortUrlCreate
) -> ShortUrl:
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
        user_id=current_user.id,
    )
    await db_short_url.insert()

    return db_short_url


