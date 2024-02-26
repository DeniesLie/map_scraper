from dataclasses import dataclass, field
from typing import List

from map_scraper.maps.domain.map_segment_tile import MapSegmentTile


@dataclass
class MapSegment:
    name: str
    zoom: float
    user_id: int
    id: int = None
    tiles: List[MapSegmentTile] = field(default_factory=list)

