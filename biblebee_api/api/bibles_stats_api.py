"""Statistics APIs for the bibles"""

from typing import List
from fastapi import APIRouter, Depends, Query
from biblebee_api.repo.bibles_repo import BiblesRepo


router = APIRouter()


## Books level stats
@router.get("/books")
async def get_books_count_by_revisions(
    revisions: List[str] = Query(["SUV"]),
    bibles_repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
):
    """Get books count by `revisions` in the querystring params"""
    cnts = await bibles_repo.get_books_count_by_revisions(revisions=revisions)
    return {"data": cnts}


@router.get("/verses")
async def get_verses_count_by_revisions(
    revisions: List[str] = Query(["SUV"]),
    bibles_repo: BiblesRepo = Depends(BiblesRepo.request_scoped),
):
    """Get verses count by `revisions` in the querystring params"""
    cnts = await bibles_repo.get_verse_counts_by_revisions(revisions=revisions)
    return {"data": cnts}
