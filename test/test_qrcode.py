import pytest
from app import app as APIAppRoot
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    with TestClient(APIAppRoot) as client:
        yield client


def test_qrcode_generate(client: TestClient):
    response = client.get("/qrcode/", params={"text": "Hello, World!", "encode": "raw"})
    assert response.status_code == 200
    assert "image/png" in response.headers["content-type"]
