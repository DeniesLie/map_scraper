from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from map_scraper.shared.exceptions import UnauthorizedException
from map_scraper.users.password_utils import verify_password
from map_scraper.users.app.queries import get_user_by_email


logger = logging.getLogger('map_scraper.users')


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str) -> bool:
    logger.info('started authentication %s', email)
    logger.debug('password: %s', password)

    user = await get_user_by_email(db, email)
    
    if user is None:
        logger.warning('user %s does not exist', email)
        raise UnauthorizedException('user with this email does not exist')

    is_authenticated = verify_password(
        password, user.hashed_password
    )

    if not is_authenticated:
        logger.warning('incorrect email or password')
        raise UnauthorizedException('incorrect email or password')

    logger.info('user %s has been successfully authenticated', email)
    return is_authenticated
