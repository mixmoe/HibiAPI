from typing import Annotated, Any

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pytest_benchmark.fixture import BenchmarkFixture


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app

    with TestClient(app, base_url="http://testserver/") as client:
        yield client


def test_openapi(client: TestClient, in_stress: bool = False):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()

    if in_stress:
        return True


def test_doc_page(client: TestClient, in_stress: bool = False):
    response = client.get("/docs")
    assert response.status_code == 200
    assert response.text

    response = client.get("/docs/test")
    assert response.status_code == 200
    assert response.text

    if in_stress:
        return True


def test_openapi_stress(client: TestClient, benchmark: BenchmarkFixture):
    assert benchmark.pedantic(
        test_openapi,
        args=(client, True),
        rounds=200,
        warmup_rounds=10,
        iterations=3,
    )


def test_doc_page_stress(client: TestClient, benchmark: BenchmarkFixture):
    assert benchmark.pedantic(
        test_doc_page, args=(client, True), rounds=200, iterations=3
    )


def test_notfound(client: TestClient):
    from hibiapi.utils.exceptions import ExceptionReturn

    response = client.get("/notexistpath")
    assert response.status_code == 404
    assert ExceptionReturn.parse_obj(response.json())


@pytest.mark.xfail(reason="not implemented yet")
def test_net_request():
    from hibiapi.utils.net import BaseNetClient
    from hibiapi.utils.routing import BaseEndpoint, SlashRouter

    test_headers = {"x-test-header": "random-string"}
    test_data = {"test": "test"}

    class TestEndpoint(BaseEndpoint):
        base = "https://httpbin.org"

        async def request(self, path: str, params: dict[str, Any]):
            url = self._join(self.base, path, params)
            response = await self.client.post(url, data=params)
            response.raise_for_status()
            return response.json()

        async def form(self, *, data: dict[str, Any]):
            return await self.request("/post", data)

        async def teapot(self):
            return await self.request("/status/{codes}", {"codes": 418})

    class TestNetClient(BaseNetClient):
        pass

    async def net_client():
        async with TestNetClient(headers=test_headers) as client:
            yield TestEndpoint(client)

    router = SlashRouter()

    @router.post("form")
    async def form(
        *,
        endpoint: Annotated[TestEndpoint, Depends(net_client)],
        data: dict[str, Any],
    ):
        return await endpoint.form(data=data)

    @router.post("teapot")
    async def teapot(endpoint: Annotated[TestEndpoint, Depends(net_client)]):
        return await endpoint.teapot()

    from hibiapi.app.routes import router as api_router

    api_router.include_router(router, prefix="/test")

    from hibiapi.app import app
    from hibiapi.utils.exceptions import ExceptionReturn

    with TestClient(app, base_url="http://testserver/api/test/") as client:
        response = client.post("form", json=test_data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["form"] == test_data
        request_headers = {k.lower(): v for k, v in response_data["headers"].items()}
        assert test_headers.items() <= request_headers.items()

        response = client.post("teapot", json=test_data)
        exception_return = ExceptionReturn.parse_obj(response.json())
        assert exception_return.code == response.status_code
