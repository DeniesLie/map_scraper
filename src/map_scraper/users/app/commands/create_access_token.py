from datetime import timedelta, datetime
from pydantic import BaseModel
from jose import jwt
import logging

from map_scraper.config import map_scraper_config


logger = logging.getLogger('map_scraper.users')


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


async def create_access_token(
        username: str,
        expires_delta: timedelta = timedelta(days=1),
    ) -> TokenResponse:
    logger.debug('started access token creation for user %s', username)

    expires_at = datetime.utcnow() + expires_delta
    payload = {
        'sub': username,
        'exp': expires_at
    }

    cfg = map_scraper_config()

    encoded_jwt = jwt.encode(
        payload,
        cfg.auth_secret_key, 
        cfg.auth_algorithm
    )

    logger.debug("generated access token for user %s, expires_at: %s, jwt: %s",
              username, expires_at, encoded_jwt)

    return TokenResponse(
        access_token=encoded_jwt, 
        token_type="bearer"
    )
