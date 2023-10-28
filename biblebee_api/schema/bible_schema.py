"""Schema module for the bible.

In this module we define data exchange format between clients to the API.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel


RT = TypeVar("RT", bound=BaseModel)


class DataResponse(
    BaseModel, Generic[RT]
):  #  pylint: disable=too-few-public-methods
    """Wrapper around responses with data type"""

    data: RT


class BibleVersionOut(BaseModel):
    """
    Model schema for data exchange of the bible version
    with the clients of the API.
    """

    version_code: str
    language: str
    russian_numbering: bool
    strong_numbers: bool
    right_to_left: bool
    chapter_string_ps: str
    year: int
    source: str

    # Optional books of the bible
    books: Optional[List["BookOut"]] = None

    class Config:  #  pylint: disable=too-few-public-methods
        """Configure BookOut model behavior"""

        from_attributes = True


class BookOut(BaseModel):
    """Base model for the bible book"""

    book_number: int
    version_code: str
    version_language: str
    short_name: str
    long_name: str
    book_color: str

    # This is optional
    # verses: List["VerseOut"] | None = None

    class Config:  #  pylint: disable=too-few-public-methods
        """Configure BookOut model behavior"""

        from_attributes = True


class VerseOut(BaseModel):
    """Model schema for a verse in the bible"""

    book_number: int
    chapter: int
    verse: int
    text: str

    class Config:  #  pylint: disable=too-few-public-methods
        """Configure VerseOut behavior"""

        from_attributes = True
