from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from app.core.config import config
from app.deps import CurrentActiveUserDep
from app.models import (
    ShortUrl,
    ShortUrlCreate,
    ShortUrlPublic,
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


@router.get("/urls/{ident}", response_model=ShortUrlPublic)
async def read_short_url(*, current_user: CurrentActiveUserDep, ident: str) -> ShortUrl:
    short_url = await ShortUrl.find(
        ShortUrl.user_id == current_user.id, ShortUrl.ident == ident
    ).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    return short_url


@router.patch("/urls/{ident}/refresh", response_model=ShortUrlPublic)
async def refresh_short_url(
    *, current_user: CurrentActiveUserDep, ident: str
) -> ShortUrl:
    short_url = await ShortUrl.find(
        ShortUrl.user_id == current_user.id, ShortUrl.ident == ident
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


@router.delete("/urls/{ident}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(*, current_user: CurrentActiveUserDep, ident: str) -> None:
    short_url = await ShortUrl.find(
        ShortUrl.user_id == current_user.id, ShortUrl.ident == ident
    ).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    await short_url.delete()
