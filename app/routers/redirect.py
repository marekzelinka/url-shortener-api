from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.models import ShortUrl

router = APIRouter(
    prefix="/redirect",
    # Hide this router from the OpenAPI docs since it's not a part of
    # the API, but rather a part of the main app
    include_in_schema=False,
)


@router.get("/{ident}")
async def redirect_by_ident(*, ident: str) -> RedirectResponse:
    short_url = await ShortUrl.find(ShortUrl.ident == ident).first_or_none()
    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with identifier {ident!r} not found",
        )

    return RedirectResponse(url=short_url.origin)
