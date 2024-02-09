from pydantic import BaseModel, conint

from map_scraper.maps import MapSegment
from map_scraper.exceptions import NotFoundException
from map_scraper.shared.contracts import Repository


class DeleteMapSegmentCommand(BaseModel):
    id: conint(ge=1)


class DeleteMapSegmentCommandHandler:
    def __init__(self, repo: Repository[MapSegment]):
        self.repo = repo

    async def __call__(self, command: DeleteMapSegmentCommand):
        map_segment = await self.repo.get(command.id)

        if map_segment is None:
            raise NotFoundException()

        await self.repo.delete(map_segment)
