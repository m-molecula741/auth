from fastapi import (
    APIRouter,
    status,
    Response,
    Request,
    Depends,
    HTTPException,
)
from app.models.auth import Token
from app.models.users import UserInDb
from app.routers.dependencies import UOWDep
from app.services.auth_service import AuthService
from app.core.base_schemas import ObjSchema
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import config
from uuid import UUID

router = APIRouter()


@router.post(path="/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login(
    uow: UOWDep,
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends(),
) -> ObjSchema:
    """Вход"""
    user = await AuthService.authenticate_user(  # type: ignore
        credentials.username, credentials.password, uow
    )
    user = UserInDb.from_orm(user)

    token = await AuthService.create_token(user, uow)
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=config.access_token_expire_minutes * 60,
        samesite="none",
        httponly=True,
        secure=True,
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=config.refresh_token_expire_days * 30 * 24 * 60,
        samesite="none",
        httponly=True,
        secure=True,
    )

    return token


@router.post(path="/refresh", status_code=status.HTTP_200_OK, response_model=Token)
async def refresh_token(
    uow: UOWDep,
    request: Request,
    response: Response,
) -> ObjSchema:
    """Обновление токенов"""
    if not request.cookies.get("refresh_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="no refresh token"
        )
    new_token = await AuthService.refresh_token(
        UUID(request.cookies.get("refresh_token")), uow
    )

    response.set_cookie(
        "access_token",
        new_token.access_token,
        max_age=config.access_token_expire_minutes * 60,
        httponly=True,
        samesite="none",
        secure=True,
    )
    response.set_cookie(
        "refresh_token",
        new_token.refresh_token,
        max_age=config.refresh_token_expire_days * 30 * 24 * 60,
        httponly=True,
        samesite="none",
        secure=True,
    )
    return new_token
