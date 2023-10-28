"""Application module"""

from fastapi import FastAPI, Request, Response

from biblebee_api.database import async_session_manager, init_tables
from biblebee_api.api import bibles_api
from biblebee_api.api import bibles_stats


def create_app():
    """Create and return an application to be deployed"""
    app = FastAPI(title="BiblebeeApi")

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        response = Response("Internal Server Error", status_code=500)
        async with async_session_manager() as manager:
            request.state.async_session = manager
            try:
                response = await call_next(request)
            finally:
                pass
            return response

    @app.on_event("startup")
    async def _init_tables():
        await init_tables()

    # Register APIs
    app.include_router(
        router=bibles_api.router,
        prefix="/api/v1/books",
        tags=["Contents"],
    )

    app.include_router(
        router=bibles_stats.router, prefix="/api/v1/stats", tags=["Statistics"]
    )

    return app
