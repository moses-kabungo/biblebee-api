"""A module for managing bible books."""

import json
from typing import Annotated, Dict, List
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from biblebee_api.repo.bibles_repo import BiblesRepo
from biblebee_api.schema.bible_schema import BookOut, DataResponse, VerseOut
from biblebee_api.service import verse_parser

router = APIRouter()
parser = verse_parser.GrammaticLexicalParser()


async def parse_verse_notation(
    query_expression: str | None = None,
) -> Dict[int, List[int]]:
    """Parse query string params and produce a dictionary of verses"""
    parser.parse(query_expression)
    return parser.get_result()


@router.get("/")
async def get_books(
    revesions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[BookOut]]:
    """List down a list of all the bible books. You must specify revisions `revisions`"""
    books = await repo.find_all(versions=revesions)
    return {"data": [BookOut.model_validate(book) for book in jsonable_encoder(books)]}


@router.get("/{book_number}/info")
async def get_book_info(
    book_number: int,
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[BookOut]]:
    """Get information about the book of the bible at `book_number` in each `revisions`"""
    books = await repo.find_book_info(book_number=book_number, revisions=revisions)
    return JSONResponse(
        {
            "data": [
                BookOut.model_validate(book).model_dump()
                for book in jsonable_encoder(books)
            ]
        }
    )


@router.get("/{book_number}/skim")
async def skim_book_content(
    book_number: int,
    parts: Annotated[
        Dict[int, List[int]],
        Depends(parse_verse_notation),
    ],
    revirsions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[VerseOut]]:
    """
    Retrieve specific Bible content by skimming through chapters and verses.

    Parameters:
    - `book_number` (int): The number of the Bible book to retrieve content from.
    - `select` (Dict[int, List[int]]): A dictionary specifying the chapters and verses to skim.
    - `revirsions` (List[str]): Optional parameter to specify Bible revisions (default is "SUV").
    """
    contents = await repo.skim_book_content(
        book_number=book_number, parts=parts, revirsions=revirsions
    )
    return JSONResponse(
        {
            "data": [
                VerseOut.model_validate(part).model_dump()
                for part in jsonable_encoder(contents)
            ]
        }
    )


@router.get("/{book_number}/verses")
async def get_book_chapters(
    book_number: int,
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[VerseOut]]:
    """Retrieve Bible content for the specific book"""
    contents = await repo.find_book_and_chapters(
        book_number=book_number, revisions=revisions
    )

    return {"data": jsonable_encoder(contents)}


@router.get("/{book_number}/chapters/{chapter}")
async def get_chapter(
    book_number: int,
    chapter: int,
    revisions: List[str] = Query(["SUV"]),
    repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
) -> DataResponse[List[VerseOut]]:
    """Retrieve Bible content for a specific chapter."""
    contents = await repo.find_chapter_verses(
        book_number=book_number, chapter=chapter, revisions=revisions, verses=[]
    )
    return JSONResponse(
        {
            "data": [
                VerseOut.model_validate(part).model_dump()
                for part in jsonable_encoder(contents)
            ]
        }
    )
