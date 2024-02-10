from functools import lru_cache

from pydantic import conint
from pydantic_settings import BaseSettings, SettingsConfigDict


class MapScraperConfig(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str
    db_url: str
    auth_secret_key: str
    auth_algorithm: str
    access_token_expire_hours: conint(ge=1)

    model_config = SettingsConfigDict(env_file='.env')


@lru_cache
def map_scraper_config(env_file: str = '.env') -> MapScraperConfig:
    return MapScraperConfig(_env_file=env_file)
