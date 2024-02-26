from typing import Callable, Any, Annotated, List
import cv2
from fastapi import FastAPI, APIRouter, Response, Depends

from map_scraper.shared.exceptions import NotFoundException
from map_scraper.shared.models import Coordinates
from map_scraper.shared.fastapi import ApiResponse
from map_scraper.users.fastapi import get_current_user
from map_scraper.users.domain import User
from map_scraper.maps.app import (
    ImportMapSegmentCommand,
    DeleteMapSegmentCommand,
    ListTilesQuery, ListMapSegmentsResponse,
    ListMapSegmentsQuery, TileResponse
)
from map_scraper.maps.fastapi import (
    create_import_map_segment_command_handler,
    create_delete_map_segment_command_handler,
    create_list_map_segments_query_handler,
    create_list_tiles_query_handler
)


def add_maps_router(app: FastAPI):
    router = APIRouter(prefix="/map-segments", tags=["map-segments"])

    @router.post("/import",
                 response_model=ApiResponse)
    async def import_map_segment(
            request: ImportMapSegmentCommand,
            user: Annotated[User, Depends(get_current_user)],
            handler: Callable[[ImportMapSegmentCommand], Any]
            = Depends(create_import_map_segment_command_handler)):
        request.user_id = user.id
        await handler(request)
        return ApiResponse.success()

    @router.get("",
                response_model=ApiResponse[List[ListMapSegmentsResponse]])
    async def list_all_map_segments(
            user: Annotated[User, Depends(get_current_user)],
            handler: Callable[[ListMapSegmentsQuery], List[ListMapSegmentsResponse]]
            = Depends(create_list_map_segments_query_handler)):
        query = ListMapSegmentsQuery(user_id=user.id)
        res = await handler(query)
        return ApiResponse[List[ListMapSegmentsResponse]].success(data=res)

    @router.delete("/{map_segment_id}",
                   response_model=ApiResponse)
    async def delete_map_segment(
            map_segment_id: int,
            user: Annotated[User, Depends(get_current_user)],
            handler: Callable[[DeleteMapSegmentCommand], Any]
            = Depends(create_delete_map_segment_command_handler)):
        command = DeleteMapSegmentCommand(id=map_segment_id, user_id=user.id)
        await handler(command)
        return ApiResponse.success()

    @router.get("/{map_segment_id}/tiles")
    async def list_map_segment_tiles(
            user: Annotated[User, Depends(get_current_user)],
            map_segment_id: int,
            start_lat: float, start_long: float,
            end_lat: float, end_long: float,
            tile_cursor: int,
            handler: Callable[[ListTilesQuery], List[TileResponse]]
            = Depends(create_list_tiles_query_handler)):
        query = ListTilesQuery(
            map_segment_id=map_segment_id, user_id=user.id,
            start=Coordinates(latitude=start_lat, longitude=start_long),
            end=Coordinates(latitude=end_lat, longitude=end_long),
            offset=tile_cursor, limit=1
        )
        tiles_res = await handler(query)

        if not any(tiles_res):
            raise NotFoundException()

        _, img = cv2.imencode('.png', tiles_res[0].img)
        return Response(
            content=img.tobytes(), media_type="image/png",
            headers={'MAP-TILE-COORDS': str(tiles_res[0].coordinates)}
        )

    app.include_router(router)
