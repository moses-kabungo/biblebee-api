"""Application module"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response

from biblebee_api.api import adm_api
from biblebee_api.api import bibles_api
from biblebee_api.api import bibles_stats_api
from biblebee_api.api import daily_verses_api
from biblebee_api.database import async_session_manager, init_tables
from biblebee_api.service import cloud_messaging


# Lifespan is used to handle heavy resource initialization
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize resources to be utilized by the api"""
    try:
        await init_tables()
        cloud_messaging.init()
        yield
    finally:
        # teardown resources.
        pass


def create_app():
    """Create and return an application to be deployed"""
    app = FastAPI(title="BiblebeeApi", lifespan=lifespan)

    @app.middleware("http")
    async def _db_session_middleware(request: Request, call_next):
        response = Response("Internal Server Error", status_code=500)
        async with async_session_manager() as manager:
            request.state.async_session = manager
            try:
                response = await call_next(request)
            finally:
                pass
            return response

    # Register APIs

    app.include_router(
        router=adm_api.router, prefix="/api/v1/admin", tags=["Admin"]
    )

    app.include_router(
        router=bibles_api.router,
        prefix="/api/v1/books",
        tags=["Contents"],
    )

    app.include_router(
        router=bibles_stats_api.router,
        prefix="/api/v1/stats",
        tags=["Statistics"],
    )

    app.include_router(
        router=daily_verses_api.router,
        prefix="/api/v1/messages",
        tags=["Daily Bible Verse"],
    )

    return app
