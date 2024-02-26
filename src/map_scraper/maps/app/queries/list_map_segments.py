from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from map_scraper.maps.domain import MapSegment


logger = logging.getLogger('map_scraper.maps')


class ListMapSegmentsQuery(BaseModel):
    user_id: int = 0


class ListMapSegmentsResponse(BaseModel):
    id: int
    name: str


class ListMapSegmentsQueryHandler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, query: ListMapSegmentsQuery) -> List[ListMapSegmentsResponse]:
        logger.info('started query')
        logger.debug('query details %s', query)

        rows = (await self.db.execute(
            select(MapSegment.id, MapSegment.name)
            .where(MapSegment.user_id == query.user_id)
        )).all()

        res = [
            ListMapSegmentsResponse(id=row.id, name=row.name)
            for row in rows
        ]

        logger.info('completed query')
        return res
