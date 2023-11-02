"""
Adminitrative APIs.

description:
-----------
Let administrators perform previledged operations
such as daily verse registrations and whitelist/blacklist
devices which should receive notifications
"""

from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from biblebee_api.repo.devices_repo import DevicesRepo
from biblebee_api.schema.bible_schema import DataResponse, DeviceIn, DeviceOut
from biblebee_api.worker import generate_daily_verse

router = APIRouter()


# An api to trigger daily bible verse generation
@router.get("/dailyverse")
async def daily_verse():
    """Generate daily bible verse"""
    task = generate_daily_verse.delay(None)
    return JSONResponse({"task_id": task.id})


@router.post("/devices")
async def add_notification_device(
    dev: DeviceIn,
    repo: Annotated[DevicesRepo, Depends(DevicesRepo.request_scoped)],
) -> DataResponse[DeviceOut]:
    """Add new notification device to the list of allowed devices."""
    saved_device = await repo.save(dev)
    return JSONResponse({"data": saved_device.model_dump()})
