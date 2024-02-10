from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import registry
import sqlalchemy

from map_scraper.config import map_scraper_config
from map_scraper.exceptions import NotFoundException
from map_scraper.maps import (
    add_maps_orm, add_maps_router
)
from map_scraper.users import (
    add_users_orm, add_users_router
)
import map_scraper.shared.infra as infra


def use_map_scraper(app: FastAPI):
    config = map_scraper_config()
    
    db_engine = create_async_engine(config.db_url, echo=True)
    async_session = async_sessionmaker(bind=db_engine)
    sqlalchemy_registry = registry()
    
    add_maps_orm(sqlalchemy_registry)
    add_users_orm(sqlalchemy_registry)
    
    add_maps_router(app)
    add_users_router(app)
    
    @app.middleware("http")
    async def error_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except NotFoundException:
            return JSONResponse(status_code=404, content="resource not found")
        except sqlalchemy.orm.exc.NoResultFound:
            return JSONResponse(status_code=404, content="resource not found")

    
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        session = async_session()
        try:
            request.state.db = session
            response = await call_next(request)
            if response.status_code == 200:
                await request.state.db.commit()
            else:
                await request.state.db.rollback()
        except Exception as e:
            await request.state.db.rollback()
            raise e
        finally:
            await session.close()
    
        return response
    
    @app.on_event("shutdown")
    async def on_server_shutdown():
        await db_engine.dispose()
        await infra.http_session.close()
