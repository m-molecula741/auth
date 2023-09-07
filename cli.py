"""Клиентская системная утилита"""
import os
from datetime import datetime

import click
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

ALEMBIC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")


@click.group()
def app_cli() -> None:
    """Контейнер для команд"""


@app_cli.group("database")
def app_database() -> None:
    """Команды ДБ"""


@app_database.command("migrate")
def migrate() -> None:
    """Миграция БД"""
    alembic_cfg = AlembicConfig(ALEMBIC_PATH)
    alembic_command.upgrade(alembic_cfg, "head")

    click.secho("Successfully migrated!", fg="green")


@app_database.command("makemigrations")
def create_migrations() -> None:
    """Create migrations migration"""
    alembic_cfg = AlembicConfig(ALEMBIC_PATH)
    alembic_command.revision(
        alembic_cfg, message=str(datetime.now().isoformat()), autogenerate=True
    )

    click.secho("Success!", fg="green")


def entrypoint() -> None:
    """Эндпоинт клиентской утилтты"""
    app_cli()


if __name__ == "__main__":
    entrypoint()
