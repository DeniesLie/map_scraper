class MapScraperException(Exception):
    def __init__(self, error: str):
        super().__init__(error)

class NotFoundException(Exception):
    pass


class MapProviderException(Exception):
    def __init__(self, error: str):
        super().__init__(error)


class UnauthorizedException(Exception):
    def __init__(self, error: str = None):
        super().__init__(error)
