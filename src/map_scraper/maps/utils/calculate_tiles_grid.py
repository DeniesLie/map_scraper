import logging
from typing import List, Tuple
from dataclasses import dataclass, field
from geopy.distance import geodesic

from map_scraper.shared.models import Coordinates


logger = logging.getLogger('map_scraper.maps')


@dataclass
class MapTilesGrid:
    tiles_width_px: int = 0
    tiles_height_px: int = 0
    coordinates: List[Tuple[float, float]] = field(default_factory=lambda: [])


def calculate_tiles_grid(
        from_coordinates: Coordinates,
        to_coordinates: Coordinates,
        zoom_m_per_px: float,
        max_tile_size_px: float) -> MapTilesGrid:
    logger.debug('calculating tiles grid: (%s, %s), zoom_m_per_px=%f, max_tile_size_px=%f',
              from_coordinates, to_coordinates, zoom_m_per_px, max_tile_size_px)

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

    logger.debug('covered area size in meters: latitude=%f, longitude=%f',
              lat_size_m, long_size_m)

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

    logger.debug('tiles grid result: lat_cells: %d, long_cells: %d, tile_size_pxs: %d x %d',
              lat_cells, long_cells, tile_size_pxs[1], tile_size_pxs[0])

    return MapTilesGrid(tile_size_pxs[0], tile_size_pxs[1], tiles_coordinates)
