from typing import Protocol, TypeVar, Optional, List, Any, Dict


T = TypeVar('T')


class Repository(Protocol[T]):
    async def list_by(self,
                load: Optional[List] = None,
                criteria: Optional[List] = None,
                order_by: Optional[Dict[str, Any]] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = None) -> List[T]:
        ...

    async def get(self, id: Any) -> Optional[T]:
        ...

    async def first(self,
              load: Optional[List] = None,
              criteria: Optional[List] = None) -> Optional[T]:
        ...

    async def one(self,
            load: Optional[List] = None,
            criteria: Optional[List] = None) -> T:
        ...

    async def any(self, *criteria) -> bool:
        ...

    def add(self, entity: T) -> None:
        ...

    async def delete(self, entity: T) -> None:
        ...
