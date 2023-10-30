"""module for the daily verses apis."""

import json
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from biblebee_api.worker import generate_daily_verse_async

router = APIRouter()


@router.get("")
async def get_daily_verse(tasks: BackgroundTasks):
    """Get daily bible verse"""

    try:
        with open("resource/daily_verse.json", "+r", encoding="utf-8") as file:
            verse = json.load(file)
    except:  # pylint: disable=bare-except
        tasks.add_task(generate_daily_verse_async, None)
        return JSONResponse("Daily verse not found", status_code=404)

    return JSONResponse(verse)
