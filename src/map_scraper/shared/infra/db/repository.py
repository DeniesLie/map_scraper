from typing import Generic, TypeVar, Type, Any, List, Optional, Dict, Sequence

from sqlalchemy import desc, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, Query

T = TypeVar('T')


class SqlAlchemyRepository(Generic[T]):
    def __init__(self, session: AsyncSession, entity_type: Type[T]):
        self.session = session
        self.entity_type = entity_type

    async def list_by(self,
                load: Optional[List] = None,
                criteria: Optional[List] = None,
                order_by: Optional[Dict[str, Any]] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = None) -> Sequence[T]:
        query = self._apply_query_params(load, criteria, order_by, offset, limit)
        return (await self.session.scalars(query)).all()

    async def get(self, _id: Any) -> Optional[T]:
        return await self.session.get(self.entity_type, _id)

    def add(self, entity: T) -> None:
        self.session.add(entity)

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)

    def _apply_query_params(self,
                            load: Optional[List] = None,
                            criteria: Optional[List] = None,
                            order_by: Optional[Dict[str, Any]] = None,
                            offset: Optional[int] = None,
                            limit: Optional[int] = None) -> Query:
        query = select(self.entity_type)

        if load:
            for relationship in load:
                query = query.options(joinedload(relationship))

        if criteria:
            for criterion in criteria:
                query = query.where(criterion)

        if order_by:
            for order, attr in order_by.items():
                if order.lower() == 'asc':
                    query = query.order_by(attr)
                elif order.lower() == 'desc':
                    query = query.order_by(desc(attr))
                else:
                    raise ValueError("Ordering direction can be 'asc' or 'desc'")

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query
