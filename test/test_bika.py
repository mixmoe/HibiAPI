from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/bika/") as client:
        client.headers["Cache-Control"] = "no-cache"
        yield client


def test_collections(client: TestClient):
    response = client.get("collections")
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_categories(client: TestClient):
    response = client.get("categories")
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_keywords(client: TestClient):
    response = client.get("keywords")
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_advanced_search(client: TestClient):
    response = client.get(
        "advanced_search", params={"keyword": "blend", "page": 1, "sort": "vd"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_category_list(client: TestClient):
    response = client.get(
        "category_list", params={"category": "全彩", "page": 1, "sort": "vd"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_author_list(client: TestClient):
    response = client.get(
        "author_list", params={"author": "ゆうき", "page": 1, "sort": "vd"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_comic_detail(client: TestClient):
    response = client.get("comic_detail", params={"id": "5873aa128fe1fa02b156863a"})
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_comic_recommendation(client: TestClient):
    response = client.get(
        "comic_recommendation", params={"id": "5873aa128fe1fa02b156863a"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_comic_episodes(client: TestClient):
    response = client.get("comic_episodes", params={"id": "5873aa128fe1fa02b156863a"})
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_comic_page(client: TestClient):
    response = client.get("comic_page", params={"id": "5873aa128fe1fa02b156863a"})
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_comic_comments(client: TestClient):
    response = client.get("comic_comments", params={"id": "5873aa128fe1fa02b156863a"})
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]


def test_games(client: TestClient):
    response = client.get("games")
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]["games"]


def test_game_detail(client: TestClient):
    response = client.get("game_detail", params={"id": "6298dc83fee4a055417cdd98"})
    assert response.status_code == 200
    assert response.json()["code"] == 200 and response.json()["data"]
