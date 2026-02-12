from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import config
from app.core.db import init_db
from app.routers import auth, redirect, urls, users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await init_db()

    yield


app = FastAPI(
    title="URL shortener RESTful API",
    description="Fast and reliable URL shortener powered by FastAPI and MongoDB.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if config.all_cors_origins:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=config.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(urls.router)
app.include_router(redirect.router)
