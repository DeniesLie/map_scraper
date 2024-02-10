from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from map_scraper.maps import MapSegment


class ListMapSegmentsQuery(BaseModel):
    user_id: int = 0


class ListMapSegmentsResponse(BaseModel):
    id: int
    name: str


class ListMapSegmentsQueryHandler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, query: ListMapSegmentsQuery) -> List[ListMapSegmentsResponse]:
        res = (await self.db.execute(
            select(MapSegment.id, MapSegment.name)
            .where(MapSegment.user_id == query.user_id)
        )).all()

        return [
            ListMapSegmentsResponse(id=row.id, name=row.name)
            for row in res
        ]
