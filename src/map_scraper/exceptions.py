class NotFoundException(Exception):
    pass


class MapProviderException(Exception):
    def __init__(self, error: str):
        super().__init__(error)
