import logging
from pydantic import BaseModel, conint, constr, Field

from map_scraper.shared.exceptions import MapProviderException
from map_scraper.maps.contracts import MapsProvider
from map_scraper.maps.domain import MapSegment, MapSegmentTile
from map_scraper.shared.models import Coordinates
from map_scraper.shared.contracts import Repository
from map_scraper.maps.utils import calculate_tiles_grid


logger = logging.getLogger('map_scraper.maps')


class ImportMapSegmentCommand(BaseModel):
    from_coordinates: Coordinates
    to_coordinates: Coordinates
    segment_name: constr(min_length=1, max_length=50)
    zoom: float
    user_id: conint(ge=1) = Field(0, hidden_from_schema=True)


class ImportMapSegmentCommandHandler:
    def __init__(self,
                 map_segment_repo: Repository[MapSegment],
                 map_provider: MapsProvider):
        self.map_segment_repo = map_segment_repo
        self.map_provider = map_provider

    async def __call__(self, command: ImportMapSegmentCommand):
        logger.info('started map segment import')
        logger.debug('command details: %s', command)

        map_segment = MapSegment(
            name=command.segment_name,
            zoom=command.zoom,
            user_id=command.user_id
        )

        zoom_m_per_px = self.map_provider.zoom_m_per_px(command.zoom)

        tiles_grid = calculate_tiles_grid(
            command.from_coordinates,
            command.to_coordinates,
            zoom_m_per_px,
            self.map_provider.max_tile_size_px()
        )

        for tile_coords in tiles_grid.coordinates:
            tile_res = await self.map_provider.load_tile(
                tile_coords, command.zoom,
                tiles_grid.tiles_width_px, tiles_grid.tiles_height_px
            )

            if tile_res.error:
                raise MapProviderException(tile_res.error)

            tile = MapSegmentTile(
                center_lat=tile_coords[0], center_long=tile_coords[1],
                img=tile_res.img
            )
            map_segment.tiles.append(tile)
            logger.debug('added tile (lat=%f, long=%f)',
                      tile.center_lat, tile.center_long)

        self.map_segment_repo.add(map_segment)
        logger.info("created map segment '%s'",
                 command.segment_name)