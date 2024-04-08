from fastapi import APIRouter, status, Depends, Response, UploadFile, File

from app.models.users import (
    UserUpdateIn,
    UserResponse,
    UserModel,
)
from app.routers.dependencies import UOWDep, get_current_active_user
from app.services.users_service import UserService
from app.services.auth_service import AuthService
from app.core.base_schemas import ObjSchema
from fastapi.responses import ORJSONResponse

router = APIRouter()


@router.post(path="/deactivate", status_code=status.HTTP_200_OK, response_model=dict)
async def deactivate_user(
    response: Response,
    uow: UOWDep,
    current_user: UserModel = Depends(get_current_active_user),
) -> dict:
    """Удалить аккаунт"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await AuthService.abort_all_sessions(current_user.id, uow)
    await UserService.deactivate_user(current_user.id, uow)
    return {"message": "User status is not active already"}


@router.patch(path="/update", status_code=status.HTTP_200_OK, response_model=bool)
async def update_user(
    user_in: UserUpdateIn,
    uow: UOWDep,
    current_user: UserModel = Depends(get_current_active_user),
) -> ORJSONResponse:
    """Изменить данные профиля"""
    is_ok = await UserService.update_user(current_user.id, user_in, uow)
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=is_ok)


@router.get(path="/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(
    uow: UOWDep,
    current_user: UserModel = Depends(get_current_active_user),
) -> ObjSchema:
    """Получить свои данные"""
    db_user = await UserService.get_user(current_user.id, uow)
    created_at_datetime = db_user.created_at
    # Преобразовать формат datetime в формат "день месяц год"
    formatted_created_at = created_at_datetime.strftime("%d %B %Y")

    return UserResponse(
        email=db_user.email,
        nickname=db_user.nickname,
        description=db_user.description,
        image_url=db_user.image_url,
        created_at=formatted_created_at,
    )


@router.patch(path="/image", status_code=status.HTTP_200_OK, response_model=str)
async def upload_image(
    uow: UOWDep,
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_active_user),
) -> str:
    """Изменение аватарки пользователя"""
    image_url = await UserService.upload_image(
        file=file, user_id=current_user.id, uow=uow
    )
    return image_url
