from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import JWTError, jwt

from map_scraper.users import User, get_user_by_email
from map_scraper.config import map_scraper_config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        request: Request,
        token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    config = map_scraper_config()

    try:
        payload = jwt.decode(token, config.auth_secret_key, algorithms=[config.auth_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(request.state.db, email)

    if user is None:
        raise credentials_exception

    return user