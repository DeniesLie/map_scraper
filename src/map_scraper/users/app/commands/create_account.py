from pydantic import BaseModel, EmailStr

from map_scraper.shared.contracts import Repository
from map_scraper.users.password_utils import hash_password
from map_scraper.users import User


class CreateAccountCommand(BaseModel):
    email: EmailStr
    password: str
    googlemaps_api_key: str


async def create_account(
        repo: Repository[User],
        command: CreateAccountCommand):
    email_exists = await repo.any(User.email == command.email)
    if email_exists:
        raise Exception('user with that email already exist')

    repo.add(User(
        email=command.email,
        hashed_password=hash_password(command.password),
        google_maps_api_key=command.googlemaps_api_key
    ))
