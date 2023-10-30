"""Worker module for the async tasks"""

import asyncio
import logging
import os
import json
from random import choice

from sqlalchemy import select
from sqlalchemy.sql import func

from celery import Celery
from biblebee_api.database import async_session_manager
from biblebee_api.model.bible_model import DailyVerse, Verse
from biblebee_api.schema.bible_schema import DailyVerseOut


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379/0"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
)


async def generate_daily_verse_async(tag: str | None) -> str:
    """Generate daily random verse."""

    # Get a random tag if tag is None
    if tag is None:
        tag = await get_random_tag()

    # Get a random daily verse matching the tag
    daily_verse = await get_random_daily_verse(tag)

    # Get and save the verse content
    verse_content = await get_verse_content(daily_verse)

    logger.debug(repr(daily_verse))

    daily_verse_out = DailyVerseOut.model_validate(daily_verse.__dict__)
    result = json.dumps(
        {"verse_content": verse_content, "ptr": daily_verse_out.model_dump()}
    )
    save_verse_to_file(result)
    return json.dumps(result)


@celery.task(name="daily_verse")
def generate_daily_verse(tag: str | None = None):
    """Generate daily bible verse"""
    return asyncio.run(generate_daily_verse_async(tag))


async def get_random_tag() -> str:
    """Get a randomly selected tag"""
    async with async_session_manager() as manager:
        async with manager() as session:
            tags_query = select(DailyVerse.tags.distinct())
            tags = (await session.execute(tags_query)).scalars().all()
            return choice(tags)


async def get_random_daily_verse(tag: str) -> DailyVerse:
    """Get a randomly tagged bible verse"""
    async with async_session_manager() as manager:
        async with manager() as session:
            query = (
                select(DailyVerse)
                .filter(DailyVerse.tags.like(f"%{tag}%"))
                .order_by(func.random())  # pylint: disable=not-callable
                .limit(1)
            )
            return (await session.execute(query)).scalars().one()


async def get_verse_content(daily_verse: DailyVerse) -> str:
    """Get content of the verse pointed by the `DailyVerse`"""
    async with async_session_manager() as manager:
        async with manager() as session:
            verse_query = select(Verse.text).filter(
                Verse.book_number == daily_verse.book_number,
                Verse.chapter == daily_verse.chapter,
                Verse.verse.between(
                    daily_verse.verse_start, daily_verse.verse_end
                ),
            )
            verse_texts = (await session.execute(verse_query)).scalars().all()
            return " ".join(verse_texts)


def save_verse_to_file(content: str):
    """Save daily verse into the"""
    with open("./resource/daily_verse.json", "w+", encoding="utf8") as file:
        file.write(content)
