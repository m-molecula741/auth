import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function", autouse=True)
def client():
    # Возвращаем тестового клиента
    with TestClient(app) as client:
        yield client
