from fastapi import HTTPException, status

from app.db.repositories.base_repo import ModelType
from app.db.uow import SqlAlchemyUnitOfWork as UOW
from app.models.auth import Token
from uuid import UUID
from datetime import datetime, timedelta, timezone
from uuid_extensions import uuid7
from app.core.config import config
from jose import jwt
from app.models.auth import AuthSessionCreate, AuthSessionUpdate
from app.models.users import UserInDb
from app.utils.users_utils import is_valid_password, is_email


class AuthService:
    @classmethod
    async def create_token(cls, user: UserInDb, uow: UOW) -> Token:
        access_token = cls._create_access_token(user)
        refresh_token_expires = timedelta(days=config.refresh_token_expire_days)
        refresh_token = cls._create_refresh_token()

        async with uow:
            ref_session, err = await uow.refresh_sessions.add(
                AuthSessionCreate(
                    user_id=user.id,
                    refresh_token=refresh_token,
                    expires_in=refresh_token_expires.total_seconds(),
                ),
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @classmethod
    async def logout(cls, token: UUID, uow: UOW) -> None:
        async with uow:
            refresh_session, err = await uow.refresh_sessions.find_one(
                refresh_token=token
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            is_ok, err = await uow.refresh_sessions.delete(
                id=refresh_session.id  # type: ignore
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    @classmethod
    async def refresh_token(cls, token: UUID, uow: UOW) -> Token:
        async with uow:
            refresh_session, err = await uow.refresh_sessions.find_refresh_session(
                refresh_token=token
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

            if refresh_session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            refresh_session_created_at = refresh_session.created_at.astimezone(
                timezone.utc
            )

            if datetime.now(timezone.utc) >= refresh_session_created_at + timedelta(
                seconds=refresh_session.expires_in
            ):
                _, err = await uow.refresh_sessions.delete(id=refresh_session.id)
                if err:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=err
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
                )

            user, err = await uow.users.find_user(id=refresh_session.user_id)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            access_token = cls._create_access_token(UserInDb.from_orm(user))
            refresh_token_expires = timedelta(days=config.refresh_token_expire_days)
            refresh_token = cls._create_refresh_token()

            _, err = await uow.refresh_sessions.update(
                id=refresh_session.id,
                obj_in=AuthSessionUpdate(
                    refresh_token=refresh_token,
                    expires_in=refresh_token_expires.total_seconds(),
                    user_id=refresh_session.user_id,
                ),
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @classmethod
    async def authenticate_user(
        cls, username: str, password: str, uow: UOW
    ) -> ModelType:
        async with uow:
            lookup_field = "email" if is_email(username) else "nickname"
            db_user, err = await uow.users.find_one(**{lookup_field: username})
            if err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
                )

        if is_valid_password(password, db_user.hashed_password):  # type: ignore
            if db_user.is_active:  # type: ignore
                return db_user  # type: ignore
            else:
                if db_user.is_verified:  # type: ignore
                    raise HTTPException(
                        status_code=status.HTTP_410_GONE, detail="account is deleted"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User is not activate",
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

    @classmethod
    async def abort_all_sessions(cls, user_id: UUID, uow: UOW) -> None:
        async with uow:
            _, err = await uow.refresh_sessions.delete_by_user_id(user_id=user_id)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    @classmethod
    def _create_access_token(cls, user: UserInDb) -> str:
        to_encode = {
            "sub": str(user.id),
            "exp": datetime.utcnow()
            + timedelta(minutes=config.access_token_expire_minutes),
            "nickname": user.nickname,
            "email": user.email,
            "is_superuser": user.is_superuser,
        }
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.algorithm
        )
        return f"Bearer {encoded_jwt}"

    @classmethod
    def _create_refresh_token(cls) -> str:
        return str(uuid7())
