from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from map_scraper.users import User

async def get_user_by_email(
        db: AsyncSession, 
        email: EmailStr) -> User:
    user_query = select(User).where(User.email == email)
    user = (await db.execute(user_query)).one_or_none()[0]
    return user
