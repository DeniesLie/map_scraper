from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from map_scraper.users.password_utils import verify_password
from map_scraper.users import (
    get_user_by_email
)


class AuthenticateUserResult(BaseModel):
    is_authenticated: bool
    error: Optional[str] = None


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str) -> AuthenticateUserResult:
    user = await get_user_by_email(db, email)
    
    if user is None:
        return AuthenticateUserResult(
            is_authenticated=False,
            error="user with this email does not exist"
        )

    is_authenticated = verify_password(
        password, user.hashed_password
    )

    if not is_authenticated:
        return AuthenticateUserResult(
            is_authenticated=False,
            error="incorrect email or password"
        )

    return AuthenticateUserResult(is_authenticated=True)
