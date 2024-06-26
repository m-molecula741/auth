from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from app.models.users import UserModel
from app.routers.dependencies import UOWDep, get_current_active_user
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(path="/logout", status_code=status.HTTP_200_OK, response_model=dict)
async def logout(
    uow: UOWDep,
    request: Request,
    response: Response,
    user: UserModel = Depends(get_current_active_user),
) -> dict:
    """Ручка Выхода"""
    response.delete_cookie("access_token", httponly=True, samesite="none", secure=True)
    response.delete_cookie("refresh_token", httponly=True, samesite="none", secure=True)

    await AuthService.logout(UUID(request.cookies.get("refresh_token")), uow)
    content = {"message": "Logged out successfully"}
    return content
