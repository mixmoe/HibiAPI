from math import inf

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/tieba/") as client:
        yield client


def test_post_list(client: TestClient):
    response = client.get("post_list", params={"name": "minecraft"})
    assert response.status_code == 200
    if response.json()["error_code"] != "0":
        pytest.xfail(reason=response.text)


def test_post_list_chinese(client: TestClient):
    # NOTE: reference https://github.com/mixmoe/HibiAPI/issues/117
    response = client.get("post_list", params={"name": "图拉丁"})
    assert response.status_code == 200
    if response.json()["error_code"] != "0":
        pytest.xfail(reason=response.text)


def test_post_detail(client: TestClient):
    response = client.get("post_detail", params={"tid": 1766018024})
    assert response.status_code == 200
    if response.json()["error_code"] != "0":
        pytest.xfail(reason=response.text)


def test_subpost_detail(client: TestClient):
    response = client.get(
        "subpost_detail", params={"tid": 1766018024, "pid": 22616319749}
    )
    assert response.status_code == 200
    assert int(response.json()["error_code"]) == 0


def test_user_profile(client: TestClient):
    response = client.get("user_profile", params={"uid": 105525655})
    assert response.status_code == 200
    assert int(response.json()["error_code"]) == 0
