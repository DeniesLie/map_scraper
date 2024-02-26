import logging

from pydantic import BaseModel, conint

from map_scraper.shared.exceptions import NotFoundException, UnauthorizedException
from map_scraper.maps.domain import MapSegment
from map_scraper.shared.contracts import Repository


logger = logging.getLogger('map_scraper.maps')


class DeleteMapSegmentCommand(BaseModel):
    id: conint(ge=1)
    user_id: conint(ge=1) = 0


class DeleteMapSegmentCommandHandler:
    def __init__(self, repo: Repository[MapSegment]):
        self.repo = repo

    async def __call__(self, command: DeleteMapSegmentCommand):
        logger.info('started deletion')
        logger.debug('command details: %s', command)

        map_segment = await self.repo.get(command.id)

        if map_segment is None:
            logger.warning('map segment with id=%d was not found', command.id)
            raise NotFoundException()

        if map_segment.user_id != command.user_id:
            logger.warning('user (id=%d) has no rights to delete map segment %s',
                        command.user_id, map_segment.name)
            raise UnauthorizedException()

        await self.repo.delete(map_segment)
        logger.info('deleting map segment id=%d', command.id)
