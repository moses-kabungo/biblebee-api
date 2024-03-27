"""Repository for the bible books (resources)"""

import logging
from typing import Dict, List


from fastapi import Request
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import func

from biblebee_api.model.bible_model import BibleRevision, Book, CrossRef, Verse
from biblebee_api.service.verse_parser import GrammaticLexicalParser


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
        self,
        async_session: async_sessionmaker[AsyncSession],
        parser: GrammaticLexicalParser,
    ) -> None:
        """Initialize books repository"""
        self.async_session = async_session
        self.parser = parser

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

    async def find_book_info(self, book_number: int, revisions: List[str]):
        """Get information related to the book in the bible given by `book_number`"""
        query = select(Book).filter_by(book_number=book_number)

        if len(revisions):
            query = query.filter(Book.version_code.in_(revisions))

        async with self.async_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def find_book_and_chapters(self, book_number: int, revisions: List[str]):
        """Get all the chapters of the book"""
        query = select(Verse).filter(Verse.book_number == book_number)

        if len(revisions):
            query = query.filter(Verse.book_version_code.in_(revisions))

        async with self.async_session() as session:
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
            query = (
                select(Verse)
                .options(selectinload(Verse.book))
                .filter(Verse.book_number == book_number)
            )

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

            print(query.compile())

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
            query = (
                select(Verse)
                .options(selectinload(Verse.book))
                .filter(Verse.book_number == book_number, Verse.chapter == chapter)
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

    async def create_cross_refs(self, cross_refs: List[CrossRef]):
        """Multiple insertion of cross references to guide the bible reader."""
        async with self.async_session() as session:
            await session.execute(delete(CrossRef))
            session.add_all(cross_refs)
            await session.commit()

        return {"message": "Cross references created successfully"}

    async def all_revisions(self) -> List[BibleRevision]:
        """Find bible revisions from the API"""
        # TODO: Add language filter
        async with self.async_session() as session:
            query = select(BibleRevision)
            result = await session.execute(query)
            return result.scalars().all()

    async def find_cross_refs(self, book_id, chapter_id, verse_id, revisions):
        """Get cross reference for the `book_id.chapter_id:verse_id` e.g., 1.1:1 (Genesis 1:1)"""
        cross_refs_query = (
            select(CrossRef)
            .filter_by(source_verse=f"{book_id}.{chapter_id}:{verse_id}")
            .order_by(CrossRef.rank.desc())
        )

        async with self.async_session() as session:
            cross_refs_result = await session.execute(cross_refs_query)
            cross_refs = cross_refs_result.scalars().all()

            verse_conditions = []

            for cross_ref in cross_refs:
                target_verses = cross_ref.target_verse.split("-")
                for verse_segment in target_verses:

                    try:
                        book_part, chapter_and_verses = verse_segment.split(".")
                        self.parser.parse(chapter_and_verses)
                        for parsed_chapter, verses in self.parser.get_result().items():
                            logger.debug(
                                "chapter: %d, verses: %s", parsed_chapter, verses
                            )
                            verse_conditions.append(
                                (int(book_part), parsed_chapter, verses)
                            )
                    except ValueError:
                        logger.error("Invalid verse segment: %s", verse_segment)
                        continue  # Skip invalid verse segment.

            # Perform a single, optimized query with collected conditions
            if len(verse_conditions) != 0:
                or_filter = or_(
                    *[
                        and_(
                            Verse.book_number == book_part,
                            Verse.chapter == chapter,
                            Verse.verse.in_(verses),
                        )
                        for book_part, chapter, verses in verse_conditions
                    ]
                )

                verses_query = select(Verse).where(or_filter)
                if len(revisions):
                    verses_query = verses_query.filter(
                        Verse.book_version_code.in_(revisions)
                    )

                # Execute final optimized query
                verses_result = await session.execute(verses_query)
                return verses_result.scalars().all()
            return []

    async def get_books_count_by_revisions(self, revisions: List[str]):
        """Returns the number of books in revirsions"""

        query = (
            select(
                Book.version_code,
                func.count().label("books_count"),  # pylint: disable=not-callable
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
                func.count().label("verses_count"),  # pylint: disable=not-callable
            )
            .select_from(Verse)
            .join(Book)
            .filter(Book.version_code.in_(revisions))
            .group_by(Book.version_code)
        )

        async with self.async_session() as session:
            result = await session.execute(query)
            return [{"revision": key, "verses_count": val} for key, val in result]

    @staticmethod
    def request_scoped(
        request: Request,
    ) -> "BiblesRepo":
        """Creates and return a data repository for managing bible books."""
        return BiblesRepo(
            async_session=request.state.async_session, parser=GrammaticLexicalParser()
        )
