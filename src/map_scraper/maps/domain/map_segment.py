from dataclasses import dataclass
from typing import List

from map_scraper.maps.domain.map_segment_tile import MapSegmentTile


@dataclass
class MapSegment:
    id: int = None

    def __init__(self, name: str, zoom: float):
        self.tiles: List[MapSegmentTile] = []
        self.name = name
        self.zoom = zoom
