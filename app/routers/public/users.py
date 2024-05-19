import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse, StreamingResponse

from app.core.base_schemas import ObjSchema
from app.models.users import (
    QueryUsers,
    UserCreateRequest,
    UserEmail,
    UserInDb,
    UserResendingEmail,
    UserResponse,
    UsersResponse,
    UserVerifyEmail,
)
from app.redis import get_redis
from app.routers.dependencies import UOWDep
from app.services.users_service import UserService
from app.utils.telegram_utils import get_image, get_image_info
from redis.asyncio import Redis

router = APIRouter()


@router.post(
    path="/registration", status_code=status.HTTP_201_CREATED, response_model=UserInDb
)
async def create_user(
    user: UserCreateRequest, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ObjSchema:
    """Регистрация пользователя"""
    return await UserService.register_new_user(uow, user, redis)


@router.patch(
    path="/registration/confirm", status_code=status.HTTP_200_OK, response_model=bool
)
async def verification_and_activation_user(
    code: UserVerifyEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    """Подтверждение регистрации"""
    is_ok = await UserService.verify_email_and_activate_user(code, uow, redis)
    if not is_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Неверный код подтверждения"
        )
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=is_ok)


@router.post(path="/resending", status_code=status.HTTP_200_OK, response_model=bool)
async def resending_email_to_user(
    resending_data: UserResendingEmail, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    """Повторная отправка кода на почту"""
    await UserService.resending_email(resending_data, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.patch(
    path="/password/reset", status_code=status.HTTP_200_OK, response_model=bool
)
async def reset_password(reset_data: UserEmail, uow: UOWDep) -> ORJSONResponse:
    """Сброс пароля"""
    await UserService.reset_password_and_send_new(reset_data, uow)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.post(path="/activate", status_code=status.HTTP_200_OK, response_model=bool)
async def activate_user(
    user_data: UserEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    """Активация пользователя"""
    await UserService.activate_user(user_data, uow, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.patch(
    path="/activate/confirm", status_code=status.HTTP_200_OK, response_model=bool
)
async def verification_and_activation(
    code: UserVerifyEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    """Подтверждение активации"""
    is_ok = await UserService.confirm_activate(code, uow, redis)
    if not is_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Неверный код подтверждения"
        )
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=is_ok)


@router.get(path="/image", status_code=status.HTTP_200_OK)
async def get_user_image(
    file_id: str,
) -> StreamingResponse:
    """Получение аватарки пользователя"""
    file_info = await get_image_info(file_id=file_id)
    file = await get_image(file_path=file_info.json()["result"]["file_path"])

    return StreamingResponse(content=io.BytesIO(file.content), media_type="image/jpeg")


@router.get(path="", status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def get_users(uow: UOWDep, query: QueryUsers = Depends()) -> UsersResponse:
    """Получение списка пользователей"""
    users_resp = await UserService.get_users(query=query, uow=uow)
    return users_resp


@router.get(path="/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_by_id(uow: UOWDep, user_id: UUID) -> UserResponse:
    """Получение пользователя по id"""
    async with uow:
        user_resp, err = await uow.users.find_one(id=user_id)
        if err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    user_resp.email = "***@mail.ru"  # type: ignore
    return UserResponse.from_orm(user_resp)
