"""Adminitrative APIs"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from biblebee_api.worker import generate_daily_verse

router = APIRouter()


# An api to trigger daily bible verse generation
@router.get("/dailyverse")
async def daily_verse():
    """Generate daily bible verse"""
    task = generate_daily_verse.delay(None)
    return JSONResponse({"task_id": task.id})
