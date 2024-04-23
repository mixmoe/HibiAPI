from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/netease/") as client:
        yield client


def test_search(client: TestClient):
    response = client.get("search", params={"s": "test"})
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["result"]["songs"]


def test_artist(client: TestClient):
    response = client.get("artist", params={"id": 1024317})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_album(client: TestClient):
    response = client.get("album", params={"id": 63263})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_detail(client: TestClient):
    response = client.get("detail", params={"id": 657666})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_detail_multiple(client: TestClient):
    response = client.get("detail", params={"id": [657666, 657667, 77185]})
    assert response.status_code == 200
    data = response.json()

    assert data["code"] == 200
    assert len(data["songs"]) == 3


def test_song(client: TestClient):
    response = client.get("song", params={"id": 657666})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_song_multiple(client: TestClient):
    response = client.get(
        "song", params={"id": (input_ids := [657666, 657667, 77185, 86369])}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["code"] == 200
    assert len(data["data"]) == len(input_ids)


def test_playlist(client: TestClient):
    response = client.get("playlist", params={"id": 39983375})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_lyric(client: TestClient):
    response = client.get("lyric", params={"id": 657666})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_mv(client: TestClient):
    response = client.get("mv", params={"id": 425588})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_mv_url(client: TestClient):
    response = client.get("mv_url", params={"id": 425588})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_comments(client: TestClient):
    response = client.get("comments", params={"id": 657666})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_record(client: TestClient):
    response = client.get("record", params={"id": 286609438})
    assert response.status_code == 200
    # TODO: test case is no longer valid
    # assert response.json()["code"] == 200


def test_djradio(client: TestClient):
    response = client.get("djradio", params={"id": 350596191})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_dj(client: TestClient):
    response = client.get("dj", params={"id": 10785929})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_detail_dj(client: TestClient):
    response = client.get("detail_dj", params={"id": 1370045285})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_user(client: TestClient):
    response = client.get("user", params={"id": 1887530069})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_user_playlist(client: TestClient):
    response = client.get("user_playlist", params={"id": 1887530069})
    assert response.status_code == 200
    assert response.json()["code"] == 200


def test_search_redirect(client: TestClient):
    response = client.get("http://testserver/netease/search", params={"s": "test"})

    assert response.status_code == 200
    assert response.history
    assert response.history[0].status_code == 301
