from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import init_db
from app.routers import urls


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await init_db()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(urls.router)
