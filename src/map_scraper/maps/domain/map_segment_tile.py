from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class MapSegmentTile:
    center_lat: float
    center_long: float
    id: Optional[int] = None
    map_segment_id: int = 0
    img: Optional[np.ndarray] = None

    def __eq__(self, other):
        if not isinstance(other, MapSegmentTile):
            return False

        if (self.id, self.map_segment_id) != (other.id, other.map_segment_id):
            return False

        return round(self.center_lat, 6) == round(other.center_lat, 6) and \
            round(self.center_long, 6) == round(other.center_long, 6)