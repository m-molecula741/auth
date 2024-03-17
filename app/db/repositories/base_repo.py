from typing import Generic, Sequence, TypeVar, get_args
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete

from app.core.base_schemas import ObjSchema
from app.core.logger import logger
from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = get_args(self.__orig_bases__[0])[0]  # type: ignore

    async def find_one(self, **filter_by) -> tuple[ModelType | None, str | None]:
        try:
            stmt = select(self.model).filter_by(**filter_by)  # type: ignore
            res = await self.session.scalar(stmt)  # type: ignore
        except Exception as e:
            logger.error(f"DB error: {e}")
            return None, f"DB error: {e}"
        if res is None:
            return None, "Data not found"

        return res, None

    async def find_all(self) -> tuple[Sequence[ModelType] | None, str | None]:
        try:
            stmt = select(self.model)
            result = await self.session.execute(stmt)
            res = result.scalars().all()
        except Exception as e:
            logger.error(f"DB error : {e}")
            return None, f"DB error : {e}"
        if res is None:
            return None, "Data not found"

        return res, None

    async def add(self, obj_in: ObjSchema) -> tuple[ModelType | None, str | None]:
        try:
            db_obj = self.model(**obj_in.dict())
            self.session.add(db_obj)
            return db_obj, None
        except Exception as e:
            logger.error(f"DB error for add object: {str(e)}")
            return None, f"DB error for add object: {str(e)}"

    async def bulk_add(
        self, obj_ins: Sequence[ObjSchema]
    ) -> tuple[list[ModelType] | None, str | None]:
        try:
            db_objs = [self.model(**obj_in.dict()) for obj_in in obj_ins]
            self.session.add_all(db_objs)
            return db_objs, None
        except Exception as e:
            logger.error(f"DB error for insert object: {str(e)}")
            return None, f"DB error for insert object: {str(e)}"

    async def update(
        self, id: int | UUID, obj_in: ObjSchema
    ) -> tuple[bool | None, str | None]:
        try:
            print(obj_in)
            stmt = update(self.model).values(**obj_in.dict()).filter_by(id=id)  # type: ignore
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"DB error from update: {e}")
            return None, f"DB error from update: {e}"
        return True, None

    async def delete(self, id: int | UUID) -> tuple[bool | None, str | None]:
        stmt = delete(self.model).where(self.model.id == id)
        try:
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"DB error for {stmt}: {str(e)}")
            return None, f"DB error for {stmt}: {str(e)}"
        return True, None
