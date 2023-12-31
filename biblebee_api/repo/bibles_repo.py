"""Repository for the bible books (resources)"""

import logging
from typing import Dict, List


from fastapi import Request
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import and_, or_, select
from sqlalchemy.sql.expression import func

from biblebee_api.model.bible_model import Book, Verse


# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BiblesRepo:  # pylint: disable=too-few-public-methods
    """
    Comprehensive data repository for managing the bible books.

    NOTE ON SEPARATION OF CONCERN:
    Extended function outside of data storage must be performed
    in a dedicated service.
    """

    def __init__(
        self, async_session: async_sessionmaker[AsyncSession]
    ) -> None:
        """Initialize books repository"""
        self.async_session = async_session

    async def find_all(self, versions: List[str]) -> List[Book]:
        """
        Finds all the books from the database.
        """
        async with self.async_session() as session:
            query = select(Book)

            if len(versions):
                query = query.filter(Book.version_code.in_(versions))

            result = await session.execute(query)

            return result.scalars().all()

    async def skim_book_content(
        self,
        book_number: int,
        parts: Dict[int, List[int]],
        revirsions: List[str],
    ) -> List[Verse]:
        """Find a list of chapters in the book"""
        async with self.async_session() as session:
            query = select(Verse).filter(Verse.book_number == book_number)

            if len(revirsions):
                query = query.filter(Verse.book_version_code.in_(revirsions))

            or_conditions = []

            for chapter, verses in parts.items():
                logger.debug("chapter: %d, verses: %s", chapter, verses)
                or_conditions.append(
                    and_(Verse.chapter == chapter, Verse.verse.in_(verses))
                )

            if len(or_conditions) != 0:
                query = query.filter(or_(*or_conditions))

            result = await session.execute(query)
            return result.scalars().all()

    async def find_chapter_verses(
        self,
        book_number: int,
        chapter: int,
        verses: List[int],
        revisions: List[str],
    ) -> List[Book]:
        """
        Find verses in the book and chapter corresponding to
        `book_number` and `chapter` respectively.
        """
        async with self.async_session() as session:
            query = select(Verse).filter(
                Verse.book_number == book_number, Verse.chapter == chapter
            )

            if len(verses):
                query = query.filter(Verse.verse.in_(verses))

            if len(revisions):
                query = query.filter(Verse.book_version_code.in_(revisions))

            query = query.order_by(Verse.book_version_code.asc())

            result = await session.execute(query)
            return result.scalars().all()

    async def find_verse(
        self, book_number: int, chapter: int, verse: int, revisions: List[str]
    ) -> List[Verse]:
        """
        Retrieves a verse in the book and chapter corresponding to
        `boo_number`, `chapter` and `verse` respectively.
        """
        async with self.async_session() as session:
            query = select(Verse).filter(
                Verse.book_number == book_number,
                Verse.chapter == chapter,
                Verse.verse == verse,
            )

            if len(revisions):
                query = query.filter(Verse.book_version_code.in_(revisions))

            result = await session.execute(query)
            return result.scalars().all()

    async def get_books_count_by_revisions(self, revisions: List[str]):
        """Returns the number of books in revirsions"""

        query = (
            select(
                Book.version_code,
                func.count().label(  # pylint: disable=not-callable
                    "books_count"
                ),
            )
            .filter(Book.version_code.in_(revisions))
            .group_by(Book.version_code)
        )

        async with self.async_session() as session:
            result = await session.execute(query)
            return [
                {"revision": row.version_code, "books_count": row.books_count}
                for row in result
            ]

    async def get_verse_counts_by_revisions(self, revisions: List[str]):
        """Get a count of verses in the revisions"""
        query = (
            select(
                Book.version_code,
                func.count().label(  # pylint: disable=not-callable
                    "verses_count"
                ),
            )
            .select_from(Verse)
            .join(Book)
            .filter(Book.version_code.in_(revisions))
            .group_by(Book.version_code)
        )

        async with self.async_session() as session:
            result = await session.execute(query)
            return [
                {"revision": key, "verses_count": val} for key, val in result
            ]

    @staticmethod
    def request_scoped(
        request: Request,
    ) -> "BiblesRepo":
        """Creates and return a data repository for managing bible books."""
        return BiblesRepo(async_session=request.state.async_session)
