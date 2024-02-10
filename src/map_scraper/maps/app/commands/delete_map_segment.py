from pydantic import BaseModel, conint

from map_scraper.maps import MapSegment
from map_scraper.exceptions import NotFoundException, UnauthorizedException
from map_scraper.shared.contracts import Repository


class DeleteMapSegmentCommand(BaseModel):
    id: conint(ge=1)
    user_id: conint(ge=1) = 0


class DeleteMapSegmentCommandHandler:
    def __init__(self, repo: Repository[MapSegment]):
        self.repo = repo

    async def __call__(self, command: DeleteMapSegmentCommand):
        map_segment = await self.repo.get(command.id)

        if map_segment.user_id != command.user_id:
            raise UnauthorizedException()

        if map_segment is None:
            raise NotFoundException()

        await self.repo.delete(map_segment)
