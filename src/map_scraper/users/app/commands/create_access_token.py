from datetime import timedelta, datetime
from pydantic import BaseModel
from jose import jwt

from map_scraper.config import map_scraper_config


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


async def create_access_token(
        username: str,
        expires_delta: timedelta = timedelta(days=1),
    ) -> TokenResponse:
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
    
    return TokenResponse(
        access_token=encoded_jwt, 
        token_type="bearer"
    )
