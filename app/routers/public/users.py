from fastapi import APIRouter, status, Depends
from fastapi.responses import ORJSONResponse

from app.models.users import (
    UserCreateRequest,
    UserInDb,
    UserVerifyEmail,
    UserResendingEmail,
    UserEmail,
)
from app.redis import get_redis
from app.routers.dependencies import UOWDep
from app.services.users_service import UserService
from app.core.base_schemas import ObjSchema
from redis.asyncio import Redis


router = APIRouter()


@router.post(
    path="/registration", status_code=status.HTTP_201_CREATED, response_model=UserInDb
)
async def create_user(
    user: UserCreateRequest, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ObjSchema:
    print("зашел")
    return await UserService.register_new_user(uow, user, redis)


@router.patch(
    path="/registration/confirm", status_code=status.HTTP_200_OK, response_model=bool
)
async def verification_and_activation_user(
    code: UserVerifyEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    is_ok = await UserService.verify_email_and_activate_user(code, uow, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=is_ok)


@router.post(path="/resending", status_code=status.HTTP_200_OK, response_model=bool)
async def resending_email_to_user(
    resending_data: UserResendingEmail, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    await UserService.resending_email(resending_data, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.patch(
    path="/password/reset", status_code=status.HTTP_200_OK, response_model=bool
)
async def reset_password(reset_data: UserEmail, uow: UOWDep) -> ORJSONResponse:
    await UserService.reset_password_and_send_new(reset_data, uow)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.post(path="/activate", status_code=status.HTTP_200_OK, response_model=bool)
async def activate_user(
    user_data: UserEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    await UserService.activate_user(user_data, uow, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=True)


@router.patch(
    path="/activate/confirm", status_code=status.HTTP_200_OK, response_model=bool
)
async def verification_and_activation(
    code: UserVerifyEmail, uow: UOWDep, redis: Redis = Depends(get_redis)
) -> ORJSONResponse:
    is_ok = await UserService.confirm_activate(code, uow, redis)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=is_ok)
