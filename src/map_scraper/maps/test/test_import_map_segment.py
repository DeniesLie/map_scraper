from unittest.mock import Mock, AsyncMock, patch
import pytest
import numpy as np

from map_scraper.shared.contracts import Repository
from map_scraper.maps.utils.calculate_tiles_grid import MapTilesGrid
from map_scraper.maps.contracts import LoadTileResult, MapsProvider
from map_scraper.maps.domain import MapSegment, MapSegmentTile
from map_scraper.maps.app.commands import (
    ImportMapSegmentCommand, ImportMapSegmentCommandHandler
)
from map_scraper.shared.exceptions import MapProviderException
from map_scraper.shared.models import Coordinates


ZOOM_M_PER_PX = 1
MAX_TILE_SIZE_PX = 500
CALCULATE_TILES_GRID_PATH = f'{ImportMapSegmentCommand.__module__}.calculate_tiles_grid'

@pytest.fixture
def map_tiles_grid() -> MapTilesGrid:
    return MapTilesGrid(
        tiles_width_px=100,
        tiles_height_px=200,
        coordinates=[(0.1, 0.2), (1.1, 1.2)]
    )

@pytest.fixture
def success_tile_res() -> LoadTileResult:
    return LoadTileResult(img=np.zeros(1))

@pytest.fixture
def error_tile_res() -> LoadTileResult:
    return LoadTileResult(error='Error')

@pytest.fixture
def import_command() -> ImportMapSegmentCommand:
    return ImportMapSegmentCommand(
        from_coordinates=Coordinates(latitude=0.1, longitude=0.2),
        to_coordinates=Coordinates(latitude=1.1, longitude=1.2),
        segment_name='test_segment',
        zoom=20,
        user_id=1
    )

@pytest.fixture
def maps_provider_mock() -> MapsProvider:
    maps_provider = Mock()
    maps_provider.zoom_m_per_px.return_value = ZOOM_M_PER_PX
    maps_provider.max_tile_size_px.return_value = MAX_TILE_SIZE_PX
    return maps_provider

@pytest.fixture
def map_segment_repo_mock() -> Repository[MapSegment]:
    return Mock()


@pytest.mark.asyncio
@patch(CALCULATE_TILES_GRID_PATH)
async def test_import_map_segment_saves_correct_map_segment_data(
    calculate_tiles_mock: Mock,
    import_command: ImportMapSegmentCommand,
    success_tile_res: LoadTileResult,
    map_tiles_grid: MapTilesGrid,
    maps_provider_mock: MapsProvider,
    map_segment_repo_mock: Repository[MapSegment]):

    # arrange
    maps_provider_mock.load_tile = AsyncMock(return_value=success_tile_res)
    calculate_tiles_mock.return_value = map_tiles_grid
    sut = ImportMapSegmentCommandHandler(map_segment_repo_mock, maps_provider_mock)

    # act
    await sut(import_command)

    # assert
    map_segment_repo_mock.add.assert_called_once_with(
        MapSegment(
            name=import_command.segment_name,
            zoom=import_command.zoom,
            user_id=import_command.user_id,
            tiles=[MapSegmentTile(center_lat=t[0], center_long=t[1])
                   for t in map_tiles_grid.coordinates]
        )
    )


@pytest.mark.asyncio
@patch(CALCULATE_TILES_GRID_PATH)
async def test_import_map_segment_passes_correct_arguments_to_calculate_tiles_grid(
    calculate_tiles_mock: Mock,
    import_command: ImportMapSegmentCommand,
    maps_provider_mock: MapsProvider,
    map_segment_repo_mock: Repository[MapSegment]):

    # arrange
    calculate_tiles_mock.return_value = MapTilesGrid()
    sut = ImportMapSegmentCommandHandler(map_segment_repo_mock, maps_provider_mock)

    # act
    await sut(import_command)

    # assert
    calculate_tiles_mock.assert_called_once_with(
        import_command.from_coordinates, import_command.to_coordinates,
        ZOOM_M_PER_PX, MAX_TILE_SIZE_PX
    )


@pytest.mark.asyncio
@patch(CALCULATE_TILES_GRID_PATH)
async def test_import_map_segment_raises_exception_on_map_provider_error_response(
    calculate_tiles_mock: Mock,
    import_command: ImportMapSegmentCommand,
    error_tile_res: LoadTileResult,
    map_tiles_grid: MapTilesGrid,
    maps_provider_mock: MapsProvider,
    map_segment_repo_mock: Repository[MapSegment]):

    # arrange
    calculate_tiles_mock.return_value = map_tiles_grid
    maps_provider_mock.load_tile = AsyncMock(return_value=error_tile_res)
    sut = ImportMapSegmentCommandHandler(map_segment_repo_mock, maps_provider_mock)

    # act / assert
    with pytest.raises(MapProviderException):
        await sut(import_command)
