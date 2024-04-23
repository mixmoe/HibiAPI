from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/bilibili/v3/") as client:
        yield client


def test_video_info(client: TestClient):
    response = client.get("video_info", params={"aid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_video_address(client: TestClient):
    response = client.get(
        "video_address",
        params={"aid": 2, "cid": 62131},
    )
    assert response.status_code == 200

    if response.json()["code"] != 0:
        pytest.xfail(reason=response.text)


def test_user_info(client: TestClient):
    response = client.get("user_info", params={"uid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_user_uploaded(client: TestClient):
    response = client.get("user_uploaded", params={"uid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.skip(reason="not implemented yet")
def test_user_favorite(client: TestClient):
    # TODO:add test case
    pass


def test_season_info(client: TestClient):
    response = client.get("season_info", params={"season_id": 425})
    assert response.status_code == 200
    assert response.json()["code"] in (0, -404)


def test_season_recommend(client: TestClient):
    response = client.get("season_recommend", params={"season_id": 425})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_season_episode(client: TestClient):
    response = client.get("season_episode", params={"episode_id": 84340})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_season_timeline(client: TestClient):
    response = client.get("season_timeline")
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search(client: TestClient):
    response = client.get("search", params={"keyword": "railgun"})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search_recommend(client: TestClient):
    response = client.get("search_recommend")
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search_suggestion(client: TestClient):
    response = client.get("search_suggestion", params={"keyword": "paperclip"})
    assert response.status_code == 200
    assert response.json()["code"] == 0
