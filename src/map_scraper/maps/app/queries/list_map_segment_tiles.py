from typing import List
import numpy as np
from pydantic import BaseModel, conint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from map_scraper.maps import MapSegmentTile
from map_scraper.shared import Coordinates
from dataclasses import dataclass


class ListTilesQuery(BaseModel):
    map_segment_id: conint(ge=1)
    start: Coordinates
    end: Coordinates
    offset: conint(ge=0)
    limit: conint(ge=1)


@dataclass
class TileResponse:
    coordinates: Coordinates
    img: np.ndarray


class ListTilesQueryHandler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, query: ListTilesQuery) -> List[TileResponse]:
        lat_interval = sorted((query.start.latitude, query.end.latitude))
        long_interval = sorted((query.start.longitude, query.end.longitude))

        db_query = (select(MapSegmentTile)
                    .where(MapSegmentTile.map_segment_id == query.map_segment_id)
                    .where(MapSegmentTile.center_lat.between(*lat_interval))
                    .where(MapSegmentTile.center_long.between(*long_interval))
                    .order_by(MapSegmentTile.center_lat.asc(), MapSegmentTile.center_long.asc())
                    .offset(query.offset).limit(query.limit))

        res = (await self.db.execute(db_query)).all()

        return [
            TileResponse(
                coordinates=Coordinates(
                    latitude=row[0].center_lat,
                    longitude=row[0].center_long
                ),
                img=row[0].img
            )
            for row in res
        ]