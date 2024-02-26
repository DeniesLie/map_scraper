from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import registry
import sqlalchemy
import logging

from map_scraper.config import map_scraper_config
from map_scraper.shared.exceptions import MapScraperException, NotFoundException, UnauthorizedException
from map_scraper.maps.infra import add_maps_orm
from map_scraper.maps.fastapi import add_maps_router
from map_scraper.shared.fastapi import ApiResponse
from map_scraper.users.infra import add_users_orm
from map_scraper.users.fastapi import add_users_router
import map_scraper.shared.infra as infra


logger = logging.getLogger('map_scraper')

def use_map_scraper(app: FastAPI):
    logger.info('adding map_scraper module to fastapi app...')

    config = map_scraper_config()

    db_engine = create_async_engine(config.db_url, echo=True)
    Session = async_sessionmaker(bind=db_engine)
    sqlalchemy_registry = registry()
    
    add_maps_orm(sqlalchemy_registry)
    add_users_orm(sqlalchemy_registry)
    
    add_maps_router(app)
    add_users_router(app)

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        session = Session()
        try:
            request.state.db = session
            response = await call_next(request)
            if response.status_code == 200:
                await request.state.db.commit()
            else:
                await request.state.db.rollback()
        except Exception as ex:
            await request.state.db.rollback()
            raise ex
        finally:
            await session.close()
    
        return response

    @app.middleware("http")
    async def error_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except (NotFoundException, sqlalchemy.orm.exc.NoResultFound):
            return JSONResponse(status_code=404, content=ApiResponse.error('resource not found').model_dump())
        except UnauthorizedException as ex:
            return JSONResponse(status_code=401, content=ApiResponse.error(str(ex)).model_dump())
        except MapScraperException as ex:
            return JSONResponse(status_code=400, content=ApiResponse.error(str(ex)).model_dump())
        except Exception:
            logger.exception('internal server error')
            return JSONResponse(status_code=500, content=ApiResponse.error('internal server error').model_dump())

    @app.on_event("shutdown")
    async def on_server_shutdown():
        await db_engine.dispose()
        await infra.http_session.close()

    logger.info('successfully added map_scraper module to fastapi app')