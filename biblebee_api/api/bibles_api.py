"""A module for managing bible books."""

from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from biblebee_api.repo.bibles_repo import BiblesRepo
from biblebee_api.schema.bible_schema import BookOut, DataResponse, VerseOut
from biblebee_api.service import verse_parser

router = APIRouter()


async def read_stops(verses: str | None = None):
    """
    Read verse stops from the query string parameters
    ```sh
    curl -X GET http://<base_url>/api/v1/books/10/chapters/49?verses=10-11,13-15
    #> Genesis 49:10-11,13-15
    ```
    """
    if verses is None:
        return []

    return verse_parser.parse_bible_verse(verse_str=verses)


@router.get("/")
async def get_books(
    revesions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[BookOut]]:
    """List down a list of all the bible books. You must specify revisions `revisions`"""
    books = await repo.find_all(versions=revesions)
    return {"data": [BookOut.model_validate(book) for book in books]}


@router.get("/{book_number}/chapters")
async def get_book_chapters(
    book_number: int,
    revirsions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[VerseOut]]:
    """
    Get a list of chapters in a book of the bible identified by `book_number`.
    You can also run a parallel comparisions by specifying `revirsions` you need
    in the query string.
    """
    chapters = await repo.find_book_chapters(
        book_number=book_number, revirsions=revirsions
    )
    return {"data": chapters}


@router.get("/{book_number}/chapters/{chapter}/verses")
async def get_chapter_verses(
    book_number: int,
    chapter: int,
    verses: Annotated[List[int], Depends(read_stops)],
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[VerseOut]]:
    """Get verses for the chapter in one of the bible books."""
    verses = await repo.find_chapter_verses(
        book_number=book_number,
        chapter=chapter,
        verses=verses,
        revisions=revisions,
    )

    return JSONResponse(
        {
            "data": [
                VerseOut.model_validate(verse).model_dump()
                for verse in jsonable_encoder(verses)
            ]
        }
    )
