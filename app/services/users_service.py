from fastapi import HTTPException, status

from app.core.base_schemas import ObjSchema
from app.db.uow import SqlAlchemyUnitOfWork as UOW
from app.models.users import (
    UserCreate,
    UserCreateRequest,
    UserInDb,
    UserDeactivate,
    UserModel,
    UserUpdateIn,
    UserUpdate,
    UserVerifyEmail,
    ActivateUser,
    UserResendingEmail,
    UserEmail,
    UserPassword,
)
from app.utils.users_utils import get_password_hash
from uuid_extensions import uuid7
from uuid import UUID
import random
from app.tasks.tasks import (
    send_register_confirmation_email,
    send_new_password_by_email,
    send_activate_code_by_email,
)
from redis.asyncio import Redis
import json


class UserService:
    @classmethod
    async def register_new_user(
        cls, uow: UOW, user: UserCreateRequest, redis: Redis
    ) -> ObjSchema:
        async with uow:
            user_exist, err = await uow.users.find_user(email=user.email)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            elif user_exist:
                if user_exist.is_verified:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User already exists",
                    )
                else:
                    _, err = await uow.users.delete(user_exist.id)
                    if err:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail=err
                        )

            db_user, err = await uow.users.add(
                UserCreate(
                    id=uuid7(),
                    email=user.email,
                    name=user.name,
                    surname=user.surname,
                    hashed_password=get_password_hash(user.password),
                ),
            )
            if err:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
                )
        code = str(random.randrange(100000, 1000000))
        await redis.set(code, json.dumps(str(db_user.id)), 60 * 10)  # type: ignore
        send_register_confirmation_email.delay(code, db_user.email)  # type: ignore

        return UserInDb.from_orm(db_user)

    @classmethod
    async def get_user(cls, user_id: UUID, uow: UOW) -> UserModel:
        async with uow:
            db_user, err = await uow.users.find_user(id=user_id)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return db_user

    @classmethod
    async def deactivate_user(cls, user_id: UUID, uow: UOW) -> None:
        async with uow:
            db_user, err = await uow.users.find_user(id=user_id)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

            if db_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            _, err = await uow.users.update(id=user_id, obj_in=UserDeactivate())
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdateIn, uow: UOW) -> bool:
        async with uow:
            db_user, err = await uow.users.find_user(id=user_id)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            if db_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            if user.password:
                user_in = UserUpdate(
                    **user.dict(exclude_unset=True),
                    hashed_password=get_password_hash(user.password),
                )
            else:
                user_in = UserUpdate(
                    **user.dict(exclude_unset=True),
                    hashed_password=db_user.hashed_password,
                )

            is_ok, err = await uow.users.update(id=user_id, obj_in=user_in)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        return is_ok

    @classmethod
    async def verify_email_and_activate_user(
        cls, code: UserVerifyEmail, uow: UOW, redis: Redis
    ) -> bool:
        async with uow:
            user_id = await redis.get(code.code)
            if user_id:
                db_user, err = await uow.users.find_one(id=UUID(json.loads(user_id)))
                if err:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=err
                    )
                _, err = await uow.users.update(
                    id=UUID(json.loads(user_id)), obj_in=ActivateUser()
                )
                if err:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=err
                    )
                return True
            else:
                return False

    @classmethod
    async def resending_email(
        cls, resending_data: UserResendingEmail, redis: Redis
    ) -> None:
        code = str(random.randrange(100000, 1000000))
        await redis.set(code, json.dumps(str(resending_data.id)), 60 * 10)
        send_register_confirmation_email.delay(code, resending_data.email)

    @classmethod
    async def reset_password_and_send_new(cls, reset_data: UserEmail, uow: UOW) -> None:
        async with uow:
            db_user, err = await uow.users.find_one(email=reset_data.email)
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            if not db_user.is_verified or not db_user.is_active:  # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account not verified or deleted",
                )
            new_password = str(random.randrange(100000, 1000000))
            _, err = await uow.users.update(
                id=db_user.id,  # type: ignore
                obj_in=UserPassword(hashed_password=get_password_hash(new_password)),
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            send_new_password_by_email.delay(new_password, db_user.email)  # type: ignore

    @classmethod
    async def activate_user(cls, user_data: UserEmail, uow: UOW, redis: Redis) -> None:
        async with uow:
            db_user, err = await uow.users.find_user(
                email=user_data.email, is_verified=True
            )
            if err:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
            if db_user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="account has not been verified",
                )

        code = str(random.randrange(100000, 1000000))
        await redis.set(code, json.dumps(str(db_user.id)), 60 * 10)
        send_activate_code_by_email.delay(code, db_user.email)

    @classmethod
    async def confirm_activate(
        cls, code: UserVerifyEmail, uow: UOW, redis: Redis
    ) -> bool:
        async with uow:
            user_email = await redis.get(code.code)
            if user_email:
                db_user, err = await uow.users.find_one(id=json.loads(user_email))
                if err:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=err
                    )
                if db_user.is_verified:  # type: ignore
                    _, err = await uow.users.update(
                        id=db_user.id, obj_in=ActivateUser()  # type: ignore
                    )
                    if err:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail=err
                        )
                return True
            else:
                return False
