from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


DataT = TypeVar('DataT')


class ApiResponse(BaseModel, Generic[DataT]):
    has_succeeded: bool
    message: Optional[str] = None
    data: Optional[DataT] = None

    @classmethod
    def success(cls, message: str = None, data: DataT = None):
        return cls(has_succeeded=True, message=message, data=data)

    @classmethod
    def error(cls, message: str = None):
        return cls(has_succeeded=False, message=message)
