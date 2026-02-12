from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.security import oauth2_scheme, verify_access_token
from app.models import User

TokenDep = Annotated[str, Depends(oauth2_scheme)]


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: TokenDep) -> User:
    username = verify_access_token(token)
    if username is None:
        raise credentials_exception

    # results = await session.execute(select(User).where(User.id == user_id))
    # user = results.scalars().first()
    user = await User.find(User.username == username).first_or_none()
    if not user:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(current_user: CurrentUserDep) -> User:
    if not current_user.is_active:
        raise credentials_exception

    return current_user


CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
