from __future__ import annotations

from datetime import datetime
from uuid import UUID as py_UUID

import sqlalchemy as sa
from fastapi import HTTPException
from humps import decamelize
from pydantic import EmailStr, validator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_schemas import ObjSchema, PaginatedResponse, PaginationSchema
from app.db.database import Base


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[py_UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(
        sa.String, nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=False)
    nickname: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(sa.String(150), nullable=True)
    image_url: Mapped[str] = mapped_column(sa.String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, default=datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(sa.Boolean, default=False)


class BaseUser(ObjSchema):
    email: EmailStr


class UserCreateRequest(BaseUser):
    password: str


class UserCreate(BaseUser):
    id: py_UUID
    nickname: str
    hashed_password: str
    is_active: bool = False
    is_verified: bool = False
    is_superuser: bool = False


class UserInDb(BaseUser):
    id: py_UUID
    nickname: str
    is_active: bool = False
    is_verified: bool = False
    is_superuser: bool = False


class UserDeactivate(ObjSchema):
    is_active: bool = False


class BaseUserUpdate(ObjSchema):
    nickname: str
    description: str | None = None


class UserUpdateIn(BaseUserUpdate):
    password: str | None = None


class UserUpdate(BaseUserUpdate):
    is_active: bool = True
    hashed_password: str


class UserResponse(BaseUser):
    id: py_UUID
    nickname: str
    description: str | None
    image_url: str | None
    created_at: datetime
    is_superuser: bool = False


class UserVerifyEmail(ObjSchema):
    code: str


class ActivateUser(ObjSchema):
    is_active: bool = True
    is_verified: bool = True


class UserResendingEmail(ObjSchema):
    id: py_UUID
    email: EmailStr


class UserEmail(ObjSchema):
    email: EmailStr


class UserPassword(ObjSchema):
    hashed_password: str


class UserImageUpdate(ObjSchema):
    image_url: str


class QueryUsers(PaginationSchema):
    nickname: str | None = None

    @validator("sort_by")
    def verify_sort_by(cls, value: str) -> str:  # noqa: N805
        """Проверка формата поля, по которому сортируется список."""
        if value is not None:
            value = decamelize(value)
            if value not in UserModel.__table__.columns:
                raise HTTPException(
                    status_code=422, detail={"sortBy": "Неверное значение"}
                )
        return value


class UsersResponse(PaginatedResponse):
    result: list[UserResponse]
