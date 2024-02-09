from fastapi import Request
from map_scraper.config import map_scraper_config
from map_scraper.shared.infra import SqlAlchemyRepository
from map_scraper.maps.infra.google_maps_provider import GoogleMapsProvider
from map_scraper.maps import (
    MapSegment,
    ImportMapSegmentCommandHandler,
    DeleteMapSegmentCommandHandler,
    ListTilesQueryHandler,
    ListMapSegmentsQueryHandler
)


def create_import_map_segment_command_handler(
        request: Request) -> ImportMapSegmentCommandHandler:
    return ImportMapSegmentCommandHandler(
        SqlAlchemyRepository(request.state.db, MapSegment),
        GoogleMapsProvider(map_scraper_config().googlemaps_api_key)
    )


def create_delete_map_segment_command_handler(
        request: Request) -> DeleteMapSegmentCommandHandler:
    return DeleteMapSegmentCommandHandler(
        SqlAlchemyRepository(request.state.db, MapSegment)
    )


def create_list_tiles_query_handler(
        request: Request) -> ListTilesQueryHandler:
    return ListTilesQueryHandler(request.state.db)


def create_list_map_segments_query_handler(
        request: Request) -> ListMapSegmentsQueryHandler:
    return ListMapSegmentsQueryHandler(request.state.db)