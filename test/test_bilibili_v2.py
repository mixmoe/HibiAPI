from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/bilibili/v2/") as client:
        yield client


def test_playurl(client: TestClient):
    response = client.get("playurl", params={"aid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_paged_playurl(client: TestClient):
    response = client.get("playurl", params={"aid": 2, "page": 1})
    assert response.status_code == 200

    if response.json()["code"] != 0:
        pytest.xfail(reason=response.text)


def test_seasoninfo(client: TestClient):
    response = client.get("seasoninfo", params={"season_id": 425})
    assert response.status_code == 200
    assert response.json()["code"] in (0, -404)


def test_seasonrecommend(client: TestClient):
    response = client.get("seasonrecommend", params={"season_id": 425})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search(client: TestClient):
    response = client.get("search", params={"keyword": "railgun"})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search_suggest(client: TestClient):
    from hibiapi.api.bilibili import SearchType

    response = client.get(
        "search", params={"keyword": "paperclip", "type": SearchType.suggest.value}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_search_hot(client: TestClient):
    from hibiapi.api.bilibili import SearchType

    response = client.get(
        "search", params={"limit": "10", "type": SearchType.hot.value}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_timeline(client: TestClient):
    from hibiapi.api.bilibili import TimelineType

    response = client.get("timeline", params={"type": TimelineType.CN.value})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_space(client: TestClient):
    response = client.get("space", params={"vmid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_archive(client: TestClient):
    response = client.get("archive", params={"vmid": 2})
    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.skip(reason="not implemented yet")
def test_favlist(client: TestClient):
    # TODO:add test case
    pass
