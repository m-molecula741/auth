from __future__ import annotations

from datetime import datetime
from uuid import UUID as py_UUID

import sqlalchemy as sa
from pydantic import Field
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_schemas import ObjSchema
from app.db.database import Base


class AuthModel(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    refresh_token: Mapped[py_UUID] = mapped_column(UUID, nullable=False, index=True)
    expires_in: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, default=datetime.utcnow, nullable=False
    )
    user_id: Mapped[py_UUID] = mapped_column(
        UUID, sa.ForeignKey("user.id", ondelete="CASCADE")
    )


class Token(ObjSchema):
    access_token: str
    refresh_token: str
    token_type: str


class AuthSessionCreate(ObjSchema):
    refresh_token: py_UUID
    expires_in: int
    user_id: py_UUID


class AuthSessionUpdate(ObjSchema):
    user_id: py_UUID | None = Field(default=None)
    refresh_token: py_UUID
    expires_in: int
