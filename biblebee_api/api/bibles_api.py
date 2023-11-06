"""A module for managing bible books."""

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
    return {"data": [BookOut.model_validate(book) for book in books]}


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
