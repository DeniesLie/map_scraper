from dataclasses import dataclass
from typing import List, Tuple
from pydantic import BaseModel, constr
from geopy.distance import geodesic

from map_scraper.maps import MapSegment, MapSegmentTile
from map_scraper.maps.contracts.maps_provider import MapsProvider
from map_scraper.shared import Coordinates
from map_scraper.shared.contracts import Repository
from map_scraper.exceptions import MapProviderException


@dataclass
class MapTilesGrid:
    tiles_width_px: int
    tiles_height_px: int
    coordinates: List[Tuple[float, float]]


def calculate_tiles_grid(
        from_coordinates: Coordinates,
        to_coordinates: Coordinates,
        zoom_m_per_px: float,
        max_tile_size_px: float) -> MapTilesGrid:

    if (from_coordinates.latitude == to_coordinates.latitude
            or from_coordinates.longitude == to_coordinates.longitude):
        raise Exception('from_coordinates and to_coordinates points must lie on different latitudes and longitudes')

    if from_coordinates.latitude < to_coordinates.latitude:
        from_coordinates.latitude, to_coordinates.latitude = to_coordinates.latitude, from_coordinates.latitude

    if from_coordinates.longitude > to_coordinates.longitude:
        from_coordinates.longitude, to_coordinates.longitude = to_coordinates.longitude, from_coordinates.longitude

    lat_size_m = geodesic(
        (from_coordinates.latitude, from_coordinates.longitude),
        (to_coordinates.latitude, from_coordinates.longitude)
    ).meters

    long_size_m = geodesic(
        (from_coordinates.latitude, from_coordinates.longitude),
        (from_coordinates.latitude, to_coordinates.longitude)
    ).meters

    max_tile_size_m = max_tile_size_px * zoom_m_per_px

    lat_cells = int(lat_size_m // max_tile_size_m) + 1
    long_cells = int(long_size_m // max_tile_size_m) + 1

    lat_step_degrees = (to_coordinates.latitude - from_coordinates.latitude) / lat_cells
    long_step_degrees = (to_coordinates.longitude - from_coordinates.longitude) / long_cells

    tile_size_pxs = (int(long_size_m / zoom_m_per_px / long_cells),
                     int(lat_size_m / zoom_m_per_px / lat_cells))

    tiles_coordinates = [
        (northern_lat + lat_step_degrees / 2, western_long + long_step_degrees / 2)
        for northern_lat in [from_coordinates.latitude + lat_step_degrees * i for i in range(lat_cells)]
        for western_long in [from_coordinates.longitude + long_step_degrees * i for i in range(long_cells)]
    ]

    return MapTilesGrid(tile_size_pxs[0], tile_size_pxs[1], tiles_coordinates)


class ImportMapSegmentCommand(BaseModel):
    from_coordinates: Coordinates
    to_coordinates: Coordinates
    segment_name: constr(min_length=1, max_length=50)
    zoom: float


class ImportMapSegmentCommandHandler:
    def __init__(self,
                 map_segment_repo: Repository[MapSegment],
                 map_provider: MapsProvider):
        self.map_segment_repo = map_segment_repo
        self.map_provider = map_provider

    async def __call__(self, command: ImportMapSegmentCommand):

        map_segment = MapSegment(
            name=command.segment_name,
            zoom=command.zoom
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

        self.map_segment_repo.add(map_segment)
