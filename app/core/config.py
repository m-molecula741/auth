"""Установка глобальных конфигов из файла .env."""
from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Загружаем глобальные конфиги переменных окружения"""

    version: str = Field(default="0.0.0")

    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    environment: str | None = Field(default=None)

    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="auth")
    postgres_db_schema: str | None = Field(default=None)

    project_name: str = Field(default="auth")

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)

    redis_cache_time: int = Field(default=600)
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    secret_key: str
    algorithm: str
    domain: str
    bot_token: str = Field(default="")
    chat_id: str = Field(default="")
    tg_domain: str = Field(default="https://api.telegram.org")

    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str

    @property
    def pg_db_creds(self) -> str:
        """Формируем строку с кредами"""
        return f"{self.postgres_user}:{self.postgres_password}"

    @property
    def db_url(self) -> str:
        """DSN c параметрами подключения к БД"""
        url = (
            f"postgresql+asyncpg://"
            f"{self.pg_db_creds}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

        return url

    @property
    def redis_cache_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/1"

    @property
    def celery_broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        """Путь к файлу .env."""

        env_file = ".env"
        # в случае если запускаю через docker-compose:
        # env_file = ".env-non-dev"


config = Settings()
