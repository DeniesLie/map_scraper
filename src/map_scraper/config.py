from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class MapScraperConfig(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str
    db_url: str
    googlemaps_api_key: str

    model_config = SettingsConfigDict(env_file='.env')


@lru_cache
def map_scraper_config(env_file: str = '.env') -> MapScraperConfig:
    return MapScraperConfig(_env_file=env_file)
