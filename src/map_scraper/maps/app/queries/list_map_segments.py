from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from map_scraper.maps import MapSegment


class ListMapSegmentsQuery(BaseModel):
    ...


class ListMapSegmentsResponse(BaseModel):
    id: int
    name: str


class ListMapSegmentsQueryHandler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, query: ListMapSegmentsQuery) -> List[ListMapSegmentsResponse]:
        db_query = select(MapSegment.id, MapSegment.name)

        res = (await self.db.execute(db_query)).all()

        return [
            ListMapSegmentsResponse(id=row.id, name=row.name)
            for row in res
        ]
