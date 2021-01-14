from concurrent.futures import ThreadPoolExecutor
from secrets import token_urlsafe
from time import sleep
from typing import List

import pytest
from app import app as APIAppRoot
from fastapi.testclient import TestClient
from requests.models import Response


@pytest.fixture(scope="package")
def client():
    with TestClient(APIAppRoot) as client:
        yield client


def test_qrcode_generate(client: TestClient):
    sleep(1)
    response = client.get(
        "/api/qrcode/",
        params={
            "text": "Hello, World!",
            "encode": "raw",
        },
    )
    assert response.status_code == 200
    assert "image/png" in response.headers["content-type"]


def test_qrcode_all(client: TestClient):
    from api.qrcode import QRCodeLevel, ReturnEncode

    encodes = [i.value for i in ReturnEncode.__members__.values()]
    levels = [i.value for i in QRCodeLevel.__members__.values()]
    responses: List[Response] = []
    for encode in encodes:
        for level in levels:
            response = client.get(
                "/qrcode/",
                params={"text": "Hello, World!", "encode": encode, "level": level},
            )
            responses.append(response)
    assert not any(map(lambda r: r.status_code != 200, responses))


def test_qrcode_stress(client: TestClient):
    executor = ThreadPoolExecutor(16)

    def request(content: str):
        response = client.get("/qrcode/", params={"text": content, "level": "H"})
        assert response.status_code == 200

    return [*executor.map(request, [token_urlsafe(32) for _ in range(128)])]
