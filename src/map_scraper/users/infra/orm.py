from sqlalchemy.orm import registry
from sqlalchemy import Table, Column, Integer, String

from map_scraper.users.domain import User


def add_users_orm(orm_registry: registry):
    users_table = Table(
        'users', orm_registry.metadata,
        Column('id', Integer, primary_key=True, autoincrement='auto'),
        Column('email', String(50), nullable=False, unique=True),
        Column('hashed_password', String(100), nullable=False),
        Column('google_maps_api_key', String(50), nullable=True)
    )
    orm_registry.map_imperatively(
        User, users_table
    )