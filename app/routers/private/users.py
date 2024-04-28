from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from fastapi.responses import ORJSONResponse

from app.core.base_schemas import ObjSchema
from app.models.users import UserModel, UserResponse, UserUpdateIn
from app.routers.dependencies import UOWDep, get_current_active_user
from app.services.auth_service import AuthService
from app.services.users_service import UserService

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
    return UserResponse.from_orm(db_user)


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
