from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr


from map_scraper.users.domain import User

import logging

logger = logging.getLogger('map_scraper.users')


async def get_user_by_email(
        db: AsyncSession, 
        email: EmailStr) -> User:
    logger.info('started query')
    logger.debug('query details: email: %s', email)

    user: User = await db.scalar(
        select(User).where(User.email == email)
    )

    logger.info('completed query')
    return user


