from dataclasses import dataclass
from typing import Protocol, Optional, Tuple

import numpy as np


@dataclass
class LoadTileResult:
    error: Optional[str] = None
    img: Optional[np.ndarray] = None


class MapsProvider(Protocol):
    async def load_tile(self,
                        center: Tuple[float, float],
                        zoom: float,
                        with_px: int, height_px: int) -> LoadTileResult:
        ...

    @staticmethod
    def zoom_m_per_px(zoom_lvl: float) -> float:
        ...

    @staticmethod
    def max_tile_size_px() -> int:
        ...
