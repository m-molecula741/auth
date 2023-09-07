from app.db.repositories.base_repo import BaseRepository, ModelType
from app.models.auth import AuthModel
from app.core.logger import logger
from sqlalchemy.sql.expression import delete
from uuid import UUID
from sqlalchemy import select


class AuthRepository(BaseRepository[AuthModel]):
    async def find_refresh_session(
        self, **filter_by
    ) -> tuple[ModelType | None, str | None]:
        try:
            stmt = select(self.model).filter_by(**filter_by)  # type: ignore
            res = await self.session.scalar(stmt)  # type: ignore
        except Exception as e:
            logger.error(f"DB error: {e}")
            return None, f"DB error: {e}"
        if res is None:
            return None, None

        return res, None

    async def delete_by_user_id(
        self, user_id: int | UUID
    ) -> tuple[bool | None, str | None]:
        stmt = delete(self.model).where(self.model.user_id == user_id)
        try:
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"DB error for {stmt}: {str(e)}")
            return None, f"DB error for {stmt}: {str(e)}"
        return True, None
