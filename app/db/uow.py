from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Type

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.logger import logger
from app.db.database import async_session_maker
from app.db.repositories import auth_repository, users_repository


class AbstractUOW(ABC):
    async def __aenter__(self) -> AbstractUOW:
        """Точка входа в контекстный менеджер"""
        raise NotImplementedError

    async def __aexit__(
        self,
        err_type: Type[BaseException] | None,
        err: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Точка выхода из контекстного менеджера"""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Сохраняем транзакцию"""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатываем транзакцию"""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUOW):
    """SQLAlchemy реализация Unit of work"""

    def __init__(self) -> None:
        """Конструктор"""
        self.session = async_session_maker()

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        """Точка входа в контекстный менеджер"""
        return self

    async def __aexit__(
        self,
        err_type: Type[BaseException] | None,
        err: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Точка выхода из контекстного менеджера"""
        if err is None:
            await self.commit()
            await self.session.close()
        else:
            await self.rollback()
            await self.session.close()
            if err_type == ValidationError:
                logger.error(str(err))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
                )

    async def commit(self) -> None:
        """Сохраняем транзакцию"""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатываем транзакцию"""
        await self.session.rollback()

    @property
    def users(self) -> users_repository.UsersRepository:
        """Доступ к репозиторию юзеров"""
        return users_repository.UsersRepository(self.session)

    @property
    def refresh_sessions(self) -> auth_repository.AuthRepository:
        """Доступ к репозиторию сессий"""
        return auth_repository.AuthRepository(self.session)
