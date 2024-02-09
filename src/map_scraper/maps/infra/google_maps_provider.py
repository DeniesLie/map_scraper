from typing import List, Tuple
import cv2
import numpy as np
from map_scraper.maps.contracts.maps_provider import LoadTileResult
import map_scraper.shared.infra as infra


_zooms_m_per_px: List[float] = [
    156543.03392,
    78271.51696,
    39135.75848,
    19567.87924,
    9783.93962,
    4891.96981,
    2445.98490,
    1222.99245,
    611.49622,
    305.74811,
    152.87405,
    76.43702,
    38.21851,
    19.10925,
    9.55462,
    4.77731,
    2.38865,
    1.19432,
    0.59716,
    0.2435625,
    0.12453125
]

_googlemaps_api_url = 'https://maps.googleapis.com/maps/api/staticmap'

class GoogleMapsProvider:
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def load_tile(self,
                        center: Tuple[float, float],
                        zoom: float,
                        with_px: int, height_px: int) -> LoadTileResult:

        params = {
            'center': f'{center[0]},{center[1]}',
            'zoom': round(zoom),
            'size': f'{with_px}x{height_px}',
            'maptype': 'satellite',
            'key': self._api_key
        }

        async with infra.http_session.get(_googlemaps_api_url, params=params) as res:
            res_bytes = await res.read()

            if res.status != 200:
                return LoadTileResult(error=res_bytes.decode())

            if len(res_bytes) == 0:
                return LoadTileResult(error='Google map_layers fastapi returned empty response body')

            image_array = np.frombuffer(res_bytes, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return LoadTileResult(img=img)

    @staticmethod
    def zoom_m_per_px(zoom_lvl: float) -> float:
        return _zooms_m_per_px[int(zoom_lvl)]

    @staticmethod
    def max_tile_size_px() -> int:
        return 640
