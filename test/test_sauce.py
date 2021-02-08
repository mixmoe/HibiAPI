from pathlib import Path

import pytest
from app import app as APIAppRoot
from fastapi.testclient import TestClient

REMOTE_SAUCE_URL = "https://i.loli.net/2021/02/08/ZF8GnifzDUAE1lc.jpg"
LOCAL_SAUCE_PATH = Path(__file__).parent / "test_sauce.jpg"


@pytest.fixture(scope="package")
def client():
    with TestClient(APIAppRoot, base_url="http://testserver/") as client:
        yield client


def test_sauce_url(client: TestClient):
    response = client.get("/api/sauce/", params={"url": REMOTE_SAUCE_URL})
    assert response.status_code == 200
    assert response.json()["header"]["status"] == 0, response.json()


def test_sauce_file(client: TestClient):
    with open(LOCAL_SAUCE_PATH, "rb") as file:
        response = client.post("/api/sauce/", files={"file": file})
    assert response.status_code == 200
    assert response.json()["header"]["status"] == 0, response.json()
