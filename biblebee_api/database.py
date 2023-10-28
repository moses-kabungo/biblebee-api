"""A module to handle database connectivity / SQLite"""

import logging
from typing import AsyncContextManager
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from biblebee_api.model.bible_model import mapper_registry

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the database URL
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./resource/SUV.SQLite3"

# Create the database engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


async def init_tables():
    """Initialize tables."""

    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)


@asynccontextmanager
async def async_session_manager() -> AsyncContextManager[
    async_sessionmaker[AsyncSession]
]:
    """Async context manager for the database connection"""
    session = async_sessionmaker(engine, expire_on_commit=True)
    try:
        yield session
    finally:
        logger.debug("Closing connection")
