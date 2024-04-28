import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt

from app.core.config import config
from app.db.uow import SqlAlchemyUnitOfWork as UOW
from app.models.users import UserModel
from app.services.users_service import UserService
from app.utils.users_utils import OAuth2PasswordBearerWithCookie

oauth2_scheme = OAuth2PasswordBearerWithCookie(token_url="/pages/profile")

UOWDep = Annotated[UOW, Depends(UOW)]


async def get_current_user(
    uow: UOW = Depends(UOW), token: str = Depends(oauth2_scheme)
) -> UserModel | None:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    current_user = await UserService.get_user(uuid.UUID(user_id), uow)
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Verify email"
        )
    return current_user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
        )
    return current_user
