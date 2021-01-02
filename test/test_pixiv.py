from datetime import date, timedelta

import pytest
from app import app as APIAppRoot
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    with TestClient(APIAppRoot) as client:
        yield client


def test_illust(client: TestClient):
    # https://www.pixiv.net/artworks/86742914
    response = client.get("/pixiv/illust", params={"id": 86742914})
    assert response.status_code == 200
    assert response.json().get("illust")


def test_member(client: TestClient):
    response = client.get("/pixiv/member", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user")


def test_member_illust(client: TestClient):
    response = client.get("/pixiv/member_illust", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("illusts") is not None


def test_favorite(client: TestClient):
    # TODO: add test case
    response = client.get("/pixiv/favorite", params={"id": 3036679})
    assert response.status_code == 200


def test_following(client: TestClient):
    response = client.get("/pixiv/following", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user_previews") is not None


def test_follower(client: TestClient):
    response = client.get("/pixiv/follower", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user_previews") is not None


def test_rank(client: TestClient):
    for i in range(2, 5):
        response = client.get(
            "/pixiv/rank", params={"date": str(date.today() - timedelta(days=i))}
        )
        assert response.status_code == 200
        assert response.json().get("illusts")


def test_search(client: TestClient):
    response = client.get("/pixiv/search", params={"word": "東方Project"})
    assert response.status_code == 200
    assert response.json().get("illusts")


def test_tags(client: TestClient):
    response = client.get("/pixiv/tags")
    assert response.status_code == 200
    assert response.json().get("trend_tags")


def test_related(client: TestClient):
    response = client.get("/pixiv/related", params={"id": 85162550})
    assert response.status_code == 200
    assert response.json().get("illusts")


def test_ugoira_metadata(client: TestClient):
    response = client.get("/pixiv/ugoira_metadata", params={"id": 85162550})
    assert response.status_code == 200
    assert response.json().get("ugoira_metadata")
