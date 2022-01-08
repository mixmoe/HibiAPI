import pytest
from fastapi.testclient import TestClient
from pytest_benchmark.fixture import BenchmarkFixture  # type:ignore


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app

    with TestClient(app, base_url="http://testserver/") as client:
        yield client


def test_openapi(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()

    return True


def test_doc_page(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200
    assert response.text

    response = client.get("/docs/test")
    assert response.status_code == 200
    assert response.text

    return True


def test_openapi_stress(client: TestClient, benchmark: BenchmarkFixture):
    assert benchmark.pedantic(
        test_openapi,
        args=(client,),
        rounds=200,
        warmup_rounds=10,
        iterations=3,
    )


def test_doc_page_stress(client: TestClient, benchmark: BenchmarkFixture):
    assert benchmark.pedantic(test_doc_page, args=(client,), rounds=200, iterations=3)


def test_notfound(client: TestClient):
    from hibiapi.utils.exceptions import ExceptionReturn

    response = client.get("/notexistpath")
    assert response.status_code == 404
    assert ExceptionReturn.parse_obj(response.json())
