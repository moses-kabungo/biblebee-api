"""Schema module for the bible.

In this module we define data exchange format between clients to the API.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict


RT = TypeVar("RT", bound=BaseModel)


class DataResponse(BaseModel, Generic[RT]):  #  pylint: disable=too-few-public-methods
    """Wrapper around responses with data type"""

    data: RT | List[RT]


class BibleRevisionOut(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Data presentation schema of the revisions
    """

    version_code: str
    version_name: str
    language: str
    russian_numbering: bool
    strong_numbers: bool
    right_to_left: bool
    chapter_string_ps: str
    year: int
    source: str


class DeviceIn(BaseModel):
    """Data transfer object that allows clients to create devices"""

    user_id: int
    token: str
    device_infos: str


class DeviceOut(BaseModel):
    """Data transfer object that allows clients to receive device info."""

    id: int
    user_id: int
    token: str
    device_infos: str
    created_at: datetime
    updated_at: datetime


class DailyVerseOut(BaseModel):  #  pylint: disable=too-few-public-methods
    """
    Model schema for the data exchange of daily bible vers
    with the clients.
    """

    id: int
    tags: str
    book_number: int
    chapter: int
    verse_start: int
    verse_end: int


class BibleVersionOut(BaseModel):  #  pylint: disable=too-few-public-methods
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

    # model config
    model_config = ConfigDict(from_attributes=True)


class BookOut(BaseModel):
    """Base model for the bible book"""

    book_number: int
    version_code: str
    version_language: str
    short_name: str
    long_name: str
    book_color: str
    chapters: int
    verses: List["VerseOut"] = []

    # This is optional
    # verses: List["VerseOut"] | None = None

    # model config
    model_config = ConfigDict(from_attributes=True)


class VerseOut(BaseModel):
    """Model schema for a verse in the bible"""

    book_version_code: str
    book_number: int
    chapter: int
    verse: int
    text: str
    book: BookOut | None = None

    # model config
    model_config = ConfigDict(from_attributes=True)


class CrossRefIn(BaseModel):
    """Model schema for creating cross reference"""

    source_verse: str
    target_verse: str
    rank: int


class CrossRefOut(BaseModel):
    """Model schema for a cross reference"""

    id: int
    source_verse: str
    target_verse: str
    rank: int

    created_at: datetime
    updated_at: datetime

    # model config
    model_config = ConfigDict(from_attributes=True)
    # pylint: disable=too-few-public-methods
