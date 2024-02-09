from typing import Callable, Any, List

import cv2
from fastapi import FastAPI, APIRouter, Depends, Response
from map_scraper.shared import Coordinates
from map_scraper.maps import (
    ImportMapSegmentCommand, create_import_map_segment_command_handler,
    DeleteMapSegmentCommand, create_delete_map_segment_command_handler,
    ListTilesQuery, TileResponse, create_list_tiles_query_handler,
    ListMapSegmentsQuery, ListMapSegmentsResponse, create_list_map_segments_query_handler
)


def add_maps_router(app: FastAPI):
    router = APIRouter(prefix="/map-segments", tags=["map-segments"])

    @router.post("/import")
    async def import_map_segment(
            request: ImportMapSegmentCommand,
            handler: Callable[[ImportMapSegmentCommand], Any]
            = Depends(create_import_map_segment_command_handler)):
        return await handler(request)

    @router.get("", response_model=ListMapSegmentsResponse)
    async def list_all_map_segments(
            handler: Callable[[ListMapSegmentsQuery], List[ListMapSegmentsResponse]]
            = Depends(create_list_map_segments_query_handler)):
        return await handler(ListMapSegmentsQuery())

    @router.delete("/{map_segment_id}")
    async def delete_map_segment(
            map_segment_id: int,
            handler: Callable[[DeleteMapSegmentCommand], Any]
            = Depends(create_delete_map_segment_command_handler)):
        command = DeleteMapSegmentCommand(map_segment_id=map_segment_id)
        return await handler(command)

    @router.get("/{map_segment_id}/tiles")
    async def list_map_segment_tiles(
            map_segment_id: int,
            start_lat: float, start_long: float,
            end_lat: float, end_long: float,
            tile_cursor: int,
            response: Response,
            handler: Callable[[ListTilesQuery], List[TileResponse]]
            = Depends(create_list_tiles_query_handler)):
        query = ListTilesQuery(
            map_segment_id=map_segment_id,
            start=Coordinates(latitude=start_lat, longitude=start_long),
            end=Coordinates(latitude=end_lat, longitude=end_long),
            offset=tile_cursor, limit=1
        )
        tiles_res = (await handler(query))[0]

        response.headers["MAP-TILE-COORDS"] = str(tiles_res.coordinates)
        _, img = cv2.imencode('.png', tiles_res.img)
        return Response(content=img.tobytes(), media_type="image/png")

    app.include_router(router)
