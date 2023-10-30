"""The module define books for the bible related information such as books and verses."""

from typing import List

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship

mapper_registry = registry()


@mapper_registry.mapped
class BibleVersion:  # pylint: disable=too-few-public-methods
    """
    Models bible version.

    The entire class represents "bible_versions" table in the DBMS.
    An instance of this class represents an entity row in the table.
    Some of the attributes in this class represents columns in the table.
    """

    __tablename__ = "bible_versions"

    version_code = mapped_column(String, primary_key=True)
    language: Mapped[str]
    russian_numbering: Mapped[bool]
    strong_numbers: Mapped[bool]
    right_to_left: Mapped[bool]
    chapter_string_ps: Mapped[str]
    year: Mapped[int]
    source: Mapped[str]

    # relationships
    books: Mapped[List["Book"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )


@mapper_registry.mapped
class Book:  # pylint: disable=too-few-public-methods
    """Models the book in the bible"""

    __tablename__ = "books"

    book_number = mapped_column(Integer, primary_key=True)
    version_code = mapped_column(
        String, ForeignKey("bible_versions.version_code")
    )
    version_language: Mapped[str]
    short_name: Mapped[str]
    long_name: Mapped[str]
    book_color: Mapped[str]

    version: Mapped["BibleVersion"] = relationship(back_populates="books")

    # Composite infos
    # book_info: Mapped[BookInfo] = composite(
    #     mapped_column("description"),
    #     mapped_column("chapter_string"),
    #     mapped_column("language"),
    #     mapped_column("russian_numbering"),
    #     mapped_column("strong_numbers"),
    #     mapped_column("right_to_left"),
    #     mapped_column("chapter_string_ps"),
    # )

    # Relationships
    verses: Mapped[List["Verse"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            "Book("
            f"\tbook_number={self.book_number},\n"
            f"\tshort_name={self.short_name},\n"
            f"\tlong_name={self.long_name},\n"
            f"\tbook_color={self.book_color},\n"
            ")"
        )


@mapper_registry.mapped
class Verse:  # pylint: disable=too-few-public-methods
    """
    Models a row entries of the verses in the 'verses' table.

    The verses are indexied in order to support FTS.
    """

    __tablename__ = "verses"

    # Composite primary key on book and verse
    verse = mapped_column(Integer, primary_key=True)
    book_number = mapped_column(
        Integer, ForeignKey("books.book_number"), primary_key=True
    )
    chapter: Mapped[int]
    text: Mapped[str]

    # Relationships (This one is important in case of Search operation)
    book: Mapped["Book"] = relationship(back_populates="verses")

    def __repr__(self) -> str:
        return (
            f"Verse(\n"
            f"\tbook_number={self.book_number},\n"
            f"\tchapter={self.chapter},\n"
            f"\tverse={self.verse},\n"
            f"\ttext={self.text}\n"
            ")"
        )


@mapper_registry.mapped
class DailyVerse:  # pylint: disable=too-few-public-methods
    """Store daily verses from the bible"""

    __tablename__ = "daily_verses"

    id = mapped_column(Integer, primary_key=True)
    tags: Mapped[str]
    book_number = mapped_column(String, ForeignKey("books.book_number"))
    chapter: Mapped[int]
    verse_start: Mapped[int]
    verse_end: Mapped[int | None]

    def __repr__(self) -> str:
        return "DailyVerse(id={!r},tags={!r},book_number={!r},chapter={!r},verse_start={!r},verse_end={!r})".format(
            self.id,
            self.tags,
            self.book_number,
            self.chapter,
            self.verse_start,
            self.verse_end,
        )
