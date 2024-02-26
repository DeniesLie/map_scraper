from typing import List
import numpy as np
from pydantic import BaseModel, conint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from map_scraper.shared.exceptions import NotFoundException, UnauthorizedException
from map_scraper.maps.domain import MapSegmentTile, MapSegment
from map_scraper.shared.models import Coordinates
from dataclasses import dataclass


logger = logging.getLogger('map_scraper.maps')


class ListTilesQuery(BaseModel):
    map_segment_id: conint(ge=1)
    start: Coordinates
    end: Coordinates
    offset: conint(ge=0)
    limit: conint(ge=1)
    user_id: conint(ge=1) = 0


@dataclass
class TileResponse:
    coordinates: Coordinates
    img: np.ndarray


class ListTilesQueryHandler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, query: ListTilesQuery) -> List[TileResponse]:
        logger.info('started query')
        logger.debug('query details: %s', query)

        lat_interval = sorted((query.start.latitude, query.end.latitude))
        long_interval = sorted((query.start.longitude, query.end.longitude))

        map_segment: MapSegment = await self.db.scalar(
            select(MapSegment)
            .where(MapSegment.id == query.map_segment_id)
        )

        if map_segment is None:
            raise NotFoundException()

        if map_segment.user_id != query.user_id:
            raise UnauthorizedException()

        tiles = await self.db.scalars(
            select(MapSegmentTile)
            .where(MapSegmentTile.map_segment_id == query.map_segment_id)
            .where(MapSegmentTile.center_lat.between(*lat_interval))
            .where(MapSegmentTile.center_long.between(*long_interval))
            .order_by(MapSegmentTile.center_lat.asc(), MapSegmentTile.center_long.asc())
            .offset(query.offset).limit(query.limit)
        )

        res = [
            TileResponse(
                coordinates=Coordinates(
                    latitude=tile.center_lat,
                    longitude=tile.center_long
                ),
                img=tile.img
            )
            for tile in tiles
        ]

        logger.info('completed query')
        return res
