from fastapi.testclient import TestClient

import cryptopilot
from cryptopilot.api.app import create_app


def test_package_is_importable() -> None:
    assert cryptopilot.__name__ == "cryptopilot"


def test_app_factory_creates_named_application() -> None:
    application = create_app()

    assert application.title == "CryptoPilot API"
    assert application.version == cryptopilot.__version__


def test_liveness_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
