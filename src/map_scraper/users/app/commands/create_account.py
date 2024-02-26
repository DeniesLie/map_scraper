from pydantic import BaseModel, EmailStr
import logging
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from map_scraper.shared.exceptions import MapScraperException
from map_scraper.users.password_utils import hash_password
from map_scraper.users.domain import User


logger = logging.getLogger('map_scraper.users')


class CreateAccountCommand(BaseModel):
    email: EmailStr
    password: str
    googlemaps_api_key: str


async def create_account(
        db: AsyncSession,
        command: CreateAccountCommand):
    logger.info('started account creation for %s', command.email)
    logger.debug('account creation details: password: %s, googlemaps_api_key: %s',
              command.password, command.googlemaps_api_key)

    email_exists: bool = await db.scalar(
        select(exists().where(User.email == command.email))
    )

    if email_exists:
        logger.warning('user with email %s already exist', command.email)
        raise MapScraperException('user with that email already exist')

    db.add(User(
        email=command.email,
        hashed_password=hash_password(command.password),
        google_maps_api_key=command.googlemaps_api_key
    ))
    logger.info('added user %s', command.email)
