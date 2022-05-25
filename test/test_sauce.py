from math import inf
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pytest_httpserver import HTTPServer

LOCAL_SAUCE_PATH = Path(__file__).parent / "test_sauce.jpg"


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/") as client:
        yield client


@pytest.mark.xfail(reason="rate limit possible reached")
def test_sauce_url(client: TestClient, httpserver: HTTPServer):
    httpserver.expect_request("/sauce").respond_with_data(LOCAL_SAUCE_PATH.read_bytes())
    response = client.get("sauce/", params={"url": httpserver.url_for("/sauce")})
    assert response.status_code == 200
    data = response.json()
    assert data["header"]["status"] == 0, data["header"]["message"]


@pytest.mark.xfail(reason="rate limit possible reached")
def test_sauce_file(client: TestClient):
    with open(LOCAL_SAUCE_PATH, "rb") as file:
        response = client.post("sauce/", files={"file": file})
    assert response.status_code == 200
    data = response.json()
    assert data["header"]["status"] == 0, data["header"]["message"]
