"""A module for managing bible books."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from biblebee_api.repo.bibles_repo import BiblesRepo
from biblebee_api.schema.bible_schema import BookOut, DataResponse, VerseOut

router = APIRouter()


@router.get("/")
async def get_books(
    versions: list[str] = Query([]),
    repo: BiblesRepo = Depends(BiblesRepo.new_instance),
) -> DataResponse[List[BookOut]]:
    """List down a list of all the bible books from the given version"""
    books = await repo.find_all(versions=versions)
    return {"data": [BookOut.model_validate(book) for book in books]}


@router.get("/{book_number}/chapters")
async def get_book_chapters(
    book_number: int,
    revirsions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.new_instance),
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
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.new_instance),
) -> DataResponse[List[VerseOut]]:
    """Get verses for the chapter in one of the bible books."""
    verses = await repo.find_chapter_verses(
        book_number=book_number, chapter=chapter, revisions=revisions
    )
    return {"data": verses}


@router.get(
    "/{book_number}/chapters/{chapter}/verses/{verse}",
    responses={404: {"detail": "Verse not found"}},
)
async def get_verse(
    book_number: int,
    chapter: int,
    verse: int,
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.new_instance),
) -> DataResponse[VerseOut]:
    """
    Gets a single verse from the book of the bible.
    You can return the same verse from multiple revisions by listing
    them in the `revisions` querystring parameter.
    """
    verse = await repo.find_verse(
        book_number=book_number,
        chapter=chapter,
        verse=verse,
        revisions=revisions,
    )

    if verse is None:
        raise HTTPException(detail="Verse not found", status_code=404)

    return {"data": verse}
