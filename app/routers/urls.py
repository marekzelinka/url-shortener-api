from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from app.models import ShortUrl, ShortUrlCreate, ShortUrlPublic

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

    expires_at = (
        (datetime.now(tz=UTC) + timedelta(days=short_url.expiration_days))
        if short_url.expiration_days
        else None
    )

    db_short_url = await ShortUrl(
        **short_url.model_dump(
            exclude={"url", "expiration_days"},
        ),
        origin=str(short_url.url),
        expires_at=expires_at,
    ).insert()

    return db_short_url
