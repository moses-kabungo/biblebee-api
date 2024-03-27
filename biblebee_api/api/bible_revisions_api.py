"""module APIs for managing bible revisions"""

from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import HTTPException

from biblebee_api.repo.bibles_repo import BiblesRepo
from biblebee_api.schema.bible_schema import BibleRevisionOut, DataResponse

router = APIRouter()


@router.get("/")
async def __get_revisions(
    bibles_repo: Annotated[BiblesRepo, Depends(BiblesRepo.request_scoped)]
) -> DataResponse[BibleRevisionOut]:
    """Get revisions from database"""
    try:
        revisions = await bibles_repo.all_revisions()
        jsonable_revisions = [
            BibleRevisionOut.model_validate(rev.__dict__) for rev in revisions
        ]
        return DataResponse(data=jsonable_revisions)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
