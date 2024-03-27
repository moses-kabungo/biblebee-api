"""Manage cross references"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException

from biblebee_api.repo.bibles_repo import BiblesRepo
from biblebee_api.schema.bible_schema import DataResponse, VerseOut

router = APIRouter()


# @router.put("/")
# async def put_cross_ref(
#     cross_refs: List[CrossRefIn],
#     bible_repo: Annotated[BiblesRepo, Depends(BiblesRepo.request_scoped)],
# ):
#     """Create cross refs"""
#     data = await bible_repo.create_cross_refs(
#         [CrossRef(**ref.model_dump()) for ref in cross_refs]
#     )
#     return {"data": data}


@router.get("/{book_id}/chapters/{chapter}/verses/{verse}")
async def get_cross_refs(
    book_id: int,
    chapter: int,
    verse: int,
    bible_repo: Annotated[BiblesRepo, Depends(BiblesRepo.request_scoped)],
    revesions: List[str] = Query(["SUV"]),
) -> DataResponse[VerseOut]:
    """Get cross references for a given book"""

    try:
        verses = await bible_repo.find_cross_refs(
            book_id=book_id, chapter_id=chapter, verse_id=verse, revisions=revesions
        )
        return {
            "data": [VerseOut.model_validate(verse).model_dump() for verse in verses]
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
