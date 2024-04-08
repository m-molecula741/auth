from fastapi.testclient import TestClient


def test_1(client: TestClient) -> None:
    assert 1 == 1
