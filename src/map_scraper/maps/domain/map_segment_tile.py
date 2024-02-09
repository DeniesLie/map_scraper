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
