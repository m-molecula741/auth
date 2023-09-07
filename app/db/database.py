"""Настройка подключения к базе данных."""
import json

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config

# Создание подключения к БД
engine = create_async_engine(
    config.db_url,
    echo=config.debug,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
)
# Создание сессии БД
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    metadata = MetaData(schema=config.postgres_db_schema)
