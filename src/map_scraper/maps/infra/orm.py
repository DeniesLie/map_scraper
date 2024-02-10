from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import registry, relationship
from sqlalchemy import TypeDecorator
from io import BytesIO
import numpy as np
from map_scraper.maps import MapSegment, MapSegmentTile


class NumpyArray(TypeDecorator):
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        np_bytes = BytesIO()
        np.save(np_bytes, value, allow_pickle=True)
        return np_bytes.getvalue()

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        np_bytes = BytesIO(value)
        return np.load(np_bytes, allow_pickle=True)


def add_maps_orm(orm_registry: registry):
    map_segments_table = Table(
        'map_segments', orm_registry.metadata,
        Column('id', Integer, primary_key=True, autoincrement='auto'),
        Column('name', String(50), nullable=False),
        Column('zoom', Float, nullable=False),
        Column('user_id', Integer,
               ForeignKey('users.id', ondelete='CASCADE'),
               nullable=False)
    )
    orm_registry.map_imperatively(
        MapSegment, map_segments_table,
        properties= {
            'zoom': map_segments_table.c.zoom,
            'tiles': relationship(MapSegmentTile, uselist=True, cascade='all'),
        }
    )

    map_segment_tiles_table = Table(
        'map_segment_tiles', orm_registry.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('center_lat', Float, nullable=False),
        Column('center_long', Float, nullable=False),
        Column('map_segment_id', Integer,
               ForeignKey('map_segments.id', ondelete='CASCADE')),
        Column('img', NumpyArray, nullable=True),
        Index('idx_map_segment_id', 'map_segment_id', unique=False),
        Index('idx_coordinates', 'center_lat', 'center_long', unique=False)
    )
    orm_registry.map_imperatively(
        MapSegmentTile, map_segment_tiles_table
    )

    