from secrets import token_urlsafe
from typing import List

import pytest
from fastapi.testclient import TestClient
from pytest_benchmark.fixture import BenchmarkFixture  # type:ignore
from requests.models import Response


@pytest.fixture(scope="package")
def client():
    from hibiapi.app import app

    with TestClient(app, base_url="http://testserver/api/") as client:
        yield client


def test_qrcode_generate(client: TestClient):
    response = client.get(
        "qrcode/",
        params={
            "text": token_urlsafe(32),
            "encode": "raw",
        },
    )
    assert response.status_code == 200
    assert "image/png" in response.headers["content-type"]
    return True


def test_qrcode_all(client: TestClient):
    from hibiapi.api.qrcode import QRCodeLevel, ReturnEncode

    encodes = [i.value for i in ReturnEncode.__members__.values()]
    levels = [i.value for i in QRCodeLevel.__members__.values()]
    responses: List[Response] = []
    for encode in encodes:
        for level in levels:
            response = client.get(
                "qrcode/",
                params={"text": "Hello, World!", "encode": encode, "level": level},
            )
            responses.append(response)
    assert not any(map(lambda r: r.status_code != 200, responses))


def test_qrcode_stress(client: TestClient, benchmark: BenchmarkFixture):
    assert benchmark.pedantic(
        test_qrcode_generate,
        args=(client,),
        rounds=50,
        iterations=3,
    )
