import re
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import config
from app.core.security import create_access_token, verify_password
from app.models import Token, User

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # Look up user by email (case-insensitive)
    user = await User.find(
        {"username": {"$regex": f"^{re.escape(form_data.username)}$", "$options": "i"}}
    ).first_or_none()
    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")
