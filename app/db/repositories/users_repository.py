from typing import Sequence

from sqlalchemy import desc, func, select

from app.consts import SortType
from app.core.logger import logger
from app.db.repositories.base_repo import BaseRepository, ModelType
from app.models.users import QueryUsers, UserModel


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

    async def get_users(
        self, query: QueryUsers
    ) -> tuple[Sequence[UserModel], int | None, str | None]:
        """Получение списка сущностей с учетом пагинации и сортировки"""
        select_count = select(func.count(self.model.id))

        stmt = select(self.model)

        if query.nickname:
            select_count = select_count.filter(
                self.model.nickname.ilike("%" + query.nickname + "%")
            )
            stmt = stmt.filter(self.model.nickname.ilike("%" + query.nickname + "%"))  # type: ignore

        # Применяем параметры пагинации
        if query.page_size is not None:
            stmt = stmt.offset((query.page - 1) * query.page_size)  # type: ignore
            stmt = stmt.limit(query.page_size)  # type: ignore

        try:
            # Проверяем, есть ли параметр для сортировки
            if query.sort_by is not None:
                sort_field = query.sort_by

                if sort_field is not None:
                    # Применяем сортировку в зависимости от указанного направления
                    if query.sort_type == SortType.desc:
                        stmt = stmt.order_by(desc(sort_field))  # type: ignore
                    else:
                        stmt = stmt.order_by(sort_field)  # type: ignore

            # Выполняем запрос
            users_count = await self.session.execute(select_count)  # type: ignore
            count = users_count.scalar()
            result = await self.session.execute(stmt)  # type: ignore
            users = result.scalars().all()
            return users, count, None
        except Exception as e:
            logger.error(f"DB error for {stmt}: {str(e)}")
            return [], None, f"DB error: {str(e)}"
