from datetime import date, timedelta
from math import inf

import pytest
from fastapi.testclient import TestClient
from pytest_benchmark.fixture import BenchmarkFixture


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app, application

    application.RATE_LIMIT_MAX = inf

    with TestClient(app, base_url="http://testserver/api/pixiv/") as client:
        client.headers["Cache-Control"] = "no-cache"
        client.headers["Accept-Language"] = "en-US,en;q=0.9"
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


def test_search_user(client: TestClient):
    response = client.get("search_user", params={"word": "鬼针草"})
    assert response.status_code == 200
    assert response.json().get("user_previews")


def test_tags(client: TestClient):
    response = client.get("tags")
    assert response.status_code == 200
    assert response.json().get("trend_tags")


def test_tags_autocomplete(client: TestClient):
    response = client.get("tags_autocomplete")
    assert response.status_code == 200
    assert response.json().get("tags")


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


def test_novel_new(client: TestClient):
    response = client.get("novel_new", params={"max_novel_id": 16002726})
    assert response.status_code == 200
    assert response.json().get("next_url")


def test_request_cache(client: TestClient, benchmark: BenchmarkFixture):
    client.headers["Cache-Control"] = "public"

    first_response = client.get("rank")
    assert first_response.status_code == 200

    second_response = client.get("rank")
    assert second_response.status_code == 200

    assert "x-cache-hit" in second_response.headers
    assert "cache-control" in second_response.headers
    assert second_response.json() == first_response.json()

    def cache_benchmark():
        response = client.get("rank")
        assert response.status_code == 200

        assert "x-cache-hit" in response.headers
        assert "cache-control" in response.headers

    benchmark.pedantic(cache_benchmark, rounds=200, iterations=3)


def test_rank_redirect(client: TestClient):
    response = client.get("/pixiv/rank")

    assert response.status_code == 200
    assert response.history
    assert response.history[0].status_code == 301


def test_rate_limit(client: TestClient):
    from hibiapi.app import application

    application.RATE_LIMIT_MAX = 1

    first_response = client.get("rank")
    assert first_response.status_code in (200, 429)

    second_response = client.get("rank")
    assert second_response.status_code == 429
    assert "retry-after" in second_response.headers
