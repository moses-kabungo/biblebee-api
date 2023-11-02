"""module to present `devices data repository`"""

from typing import List
from fastapi import Request
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
)

from biblebee_api.model.bible_model import Device
from biblebee_api.schema.bible_schema import DeviceIn, DeviceOut


class DevicesRepo:
    """data repository for the user devices."""

    def __init__(
        self, async_session: async_sessionmaker[AsyncSession]
    ) -> None:
        """initialize devices repository"""
        self.async_session = async_session

    def __query_by_token(self, token: str):
        """Produces a select statement"""
        return select(Device).filter(Device.token == token)

    def __query_by_user_id(self, user_id: int):
        """Produces a select statement"""
        return select(Device).filter(Device.user_id == user_id)

    async def __upsert(self, device: Device, session: AsyncSession):
        """Performs an upsert operation"""

        query = self.__query_by_token(device.token)
        old = (await session.execute(query)).scalars().one()

        if not old is None:
            await session.add(device)
            await session.refresh(device)
        else:
            device.device_infos = device.device_infos
            await session.flush()

        return device

    async def save(self, device: DeviceIn):
        """Save device info"""
        async with self.async_session() as session, session.begin() as trx:
            await self.__upsert(Device(**device.model_dump()), trx)
            return DeviceOut.model_validate(jsonable_encoder(device))

    async def all_tokens(self):
        """Get device tokens"""
        async with self.async_session() as session:
            result = await session.execute(select(Device.token))
            return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> List[DeviceOut]:
        """Get device by user id"""
        async with self.async_session() as session:
            result = await session.execute(self.__query_by_user_id(user_id))
            model = result.scalar_one()
            return DeviceOut.model_validate(jsonable_encoder(model))

    def request_scoped(self, req: Request):
        """
        Return an instance of the repository to be used in the context of scope lifecyle
        """
        return DevicesRepo(req.state.async_session)
