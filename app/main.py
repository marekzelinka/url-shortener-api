import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import config
from app.core.db import init_db
from app.core.security import hash_password
from app.models import User
from app.routers import auth, redirect, urls, users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await init_db()

    superuser = await User.find(
        {
            "username": {
                "$regex": f"^{re.escape(config.first_superuser)}$",
                "$options": "i",
            },
            "email": {
                "$regex": f"^{re.escape(config.first_superuser_email)}$",
                "$options": "i",
            },
        }
    ).first_or_none()
    if not superuser:
        await User(
            username=config.first_superuser,
            email=config.first_superuser_email.lower(),
            password_hash=hash_password(
                config.first_superuser_password.get_secret_value()
            ),
            is_superuser=True,
        ).insert()

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
