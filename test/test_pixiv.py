from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app

    with TestClient(app, base_url="http://testserver/api/pixiv/") as client:
        yield client


def test_illust(client: TestClient):
    # https://www.pixiv.net/artworks/86742914
    response = client.get("illust", params={"id": 86742914})
    assert response.status_code == 200
    assert response.json().get("illust")


def test_member(client: TestClient):
    response = client.get("member", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user")


def test_member_illust(client: TestClient):
    response = client.get("member_illust", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("illusts") is not None


def test_favorite(client: TestClient):
    response = client.get("favorite", params={"id": 3036679})
    assert response.status_code == 200


def test_following(client: TestClient):
    response = client.get("following", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user_previews") is not None


def test_follower(client: TestClient):
    response = client.get("follower", params={"id": 3036679})
    assert response.status_code == 200
    assert response.json().get("user_previews") is not None


def test_rank(client: TestClient):
    for i in range(2, 5):
        response = client.get(
            "rank", params={"date": str(date.today() - timedelta(days=i))}
        )
        assert response.status_code == 200
        assert response.json().get("illusts")


def test_search(client: TestClient):
    response = client.get("search", params={"word": "東方Project"})
    assert response.status_code == 200
    assert response.json().get("illusts")


def test_tags(client: TestClient):
    response = client.get("tags")
    assert response.status_code == 200
    assert response.json().get("trend_tags")


def test_related(client: TestClient):
    response = client.get("related", params={"id": 85162550})
    assert response.status_code == 200
    assert response.json().get("illusts")


def test_ugoira_metadata(client: TestClient):
    response = client.get("ugoira_metadata", params={"id": 85162550})
    assert response.status_code == 200
    assert response.json().get("ugoira_metadata")


def test_member_novel(client: TestClient):
    response = client.get("member_novel", params={"id": 14883165})
    assert response.status_code == 200
    assert response.json().get("novels")


def test_novel_series(client: TestClient):
    response = client.get("novel_series", params={"id": 1496457})
    assert response.status_code == 200
    assert response.json().get("novels")


def test_novel_detail(client: TestClient):
    response = client.get("novel_detail", params={"id": 14617902})
    assert response.status_code == 200
    assert response.json().get("novel")


def test_novel_text(client: TestClient):
    response = client.get("novel_text", params={"id": 14617902})
    assert response.status_code == 200
    assert response.json().get("novel_text")


def test_search_novel(client: TestClient):
    response = client.get("search_novel", params={"word": "碧蓝航线"})
    assert response.status_code == 200
    assert response.json().get("novels")
