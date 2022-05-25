from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/wallpaper/") as client:
        client.headers["Cache-Control"] = "no-cache"
        yield client


def test_wallpaper(client: TestClient):
    response = client.get("wallpaper", params={"category": "girl"})
    assert response.status_code == 200
    assert response.json().get("msg") == "success"


def test_wallpaper_limit(client: TestClient):
    response = client.get("wallpaper", params={"category": "girl", "limit": "21"})

    assert response.status_code == 200
    assert response.json()["msg"] == "success"
    assert len(response.json()["res"]["wallpaper"]) == 21


def test_wallpaper_skip(client: TestClient):
    response_1 = client.get(
        "wallpaper", params={"category": "girl", "limit": "20", "skip": "20"}
    )
    response_2 = client.get(
        "wallpaper", params={"category": "girl", "limit": "40", "skip": "0"}
    )

    assert response_1.status_code == 200 and response_2.status_code == 200
    assert (
        response_1.json()["res"]["wallpaper"][0]["id"]
        == response_2.json()["res"]["wallpaper"][20]["id"]
    )


def test_vertical(client: TestClient):
    response = client.get("vertical", params={"category": "girl"})
    assert response.status_code == 200
    assert response.json().get("msg") == "success"


def test_vertical_limit(client: TestClient):
    response = client.get("vertical", params={"category": "girl", "limit": "21"})
    assert response.status_code == 200
    assert response.json().get("msg") == "success"
    assert len(response.json()["res"]["vertical"]) == 21


def test_vertical_skip(client: TestClient):
    response_1 = client.get(
        "vertical", params={"category": "girl", "limit": "20", "skip": "20"}
    )
    response_2 = client.get(
        "vertical", params={"category": "girl", "limit": "40", "skip": "0"}
    )

    assert response_1.status_code == 200 and response_2.status_code == 200
    assert (
        response_1.json()["res"]["vertical"][0]["id"]
        == response_2.json()["res"]["vertical"][20]["id"]
    )
