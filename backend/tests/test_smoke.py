import json

import pytest
from fastapi.testclient import TestClient

import cryptopilot
from cryptopilot.api.app import create_app
from cryptopilot.core.settings import AppSettings, Environment


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


def test_app_factory_preserves_injected_settings() -> None:
    settings = AppSettings(environment=Environment.TEST)

    application = create_app(settings=settings)

    assert application.state.settings is settings
    assert application.state.settings.environment is Environment.TEST


def test_application_lifecycle_emits_structured_events(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = AppSettings(environment=Environment.TEST)

    with TestClient(create_app(settings=settings)):
        pass

    output = capsys.readouterr().out
    events = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    events_by_name = {event["event"]: event for event in events}

    startup_event = events_by_name["application_started"]

    assert startup_event["environment"] == "test"
    assert startup_event["execution_mode"] == "research_only"
    assert startup_event["level"] == "info"
    assert "application_stopped" in events_by_name
