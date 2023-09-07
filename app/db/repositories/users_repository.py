from app.db.repositories.base_repo import BaseRepository, ModelType
from app.models.users import UserModel
from app.core.logger import logger
from sqlalchemy import select


class UsersRepository(BaseRepository[UserModel]):
    async def find_user(self, **filter_by) -> tuple[ModelType | None, str | None]:
        try:
            stmt = select(self.model).filter_by(**filter_by)  # type: ignore
            res = await self.session.scalar(stmt)  # type: ignore
        except Exception as e:
            logger.error(f"DB error: {e}")
            return None, f"DB error: {e}"
        if res is None:
            return None, None

        return res, None
