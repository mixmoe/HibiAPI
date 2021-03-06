import pytest
from fastapi.testclient import TestClient
from src.app import app as APIAppRoot


@pytest.fixture(scope="package")
def client():
    with TestClient(APIAppRoot, base_url="http://testserver/") as client:
        yield client


def test_openapi(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()


def test_notfound(client: TestClient):
    from src.utils.exceptions import ExceptionReturn

    response = client.get("/notexistpath")
    assert response.status_code == 404
    assert ExceptionReturn.parse_obj(response.json())
