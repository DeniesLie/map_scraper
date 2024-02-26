from typing import Protocol, TypeVar, Optional, List, Sequence, Any, Dict


T = TypeVar('T')


class Repository(Protocol[T]):
    async def list_by(self,
                load: Optional[List] = None,
                criteria: Optional[List] = None,
                order_by: Optional[Dict[str, Any]] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = None) -> Sequence[T]:
        ...

    async def get(self, _id: Any) -> Optional[T]:
        ...

    def add(self, entity: T) -> None:
        ...

    async def delete(self, entity: T) -> None:
        ...
