from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import RedirectResponse

from app.models import ShortUrl

router = APIRouter(
    prefix="/redirect",
    # Hide this router from the OpenAPI docs since it's not a part of
    # the API, but rather a part of the main app
    include_in_schema=False,
)


async def update_short_url_visit_count(*, short_url: ShortUrl) -> None:
    short_url.views += 1
    short_url.last_visit_at = datetime.now(tz=UTC)

    await short_url.save_changes()


@router.get("/{ident}")
async def redirect_by_ident(*, worker: BackgroundTasks, ident: str) -> RedirectResponse:
    short_url = await ShortUrl.find(ShortUrl.ident == ident).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )
    if short_url.expires_at and short_url.expires_at < datetime.now(tz=UTC):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Short URL with identifier {ident!r} has expired",
        )

    worker.add_task(update_short_url_visit_count, short_url=short_url)

    return RedirectResponse(url=short_url.origin)
