from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pytest_httpserver import HTTPServer  # type: ignore

LOCAL_SAUCE_PATH = Path(__file__).parent / "test_sauce.jpg"


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app

    with TestClient(app, base_url="http://testserver/api/") as client:
        yield client


def test_sauce_url(client: TestClient, httpserver: HTTPServer):
    httpserver.expect_request("/sauce").respond_with_data(LOCAL_SAUCE_PATH.read_bytes())
    response = client.get("sauce/", params={"url": httpserver.url_for("/sauce")})
    assert response.status_code == 200
    if (data := response.json())["header"]["status"] == -2:
        pytest.skip(data["header"]["message"])
    assert data["header"]["status"] == 0, data["header"]["message"]


def test_sauce_file(client: TestClient):
    with open(LOCAL_SAUCE_PATH, "rb") as file:
        response = client.post("sauce/", files={"file": file})
    assert response.status_code == 200
    if (data := response.json())["header"]["status"] == -2:
        pytest.skip(data["header"]["message"])
    assert data["header"]["status"] == 0, data["header"]["message"]
