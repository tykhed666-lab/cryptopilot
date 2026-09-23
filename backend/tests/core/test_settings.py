import pytest
from pydantic import ValidationError

from cryptopilot.core.settings import AppSettings, Environment, ExecutionMode

SETTINGS_ENVIRONMENT_VARIABLES = (
    "CRYPTOPILOT_ENVIRONMENT",
    "CRYPTOPILOT_EXECUTION_MODE",
    "CRYPTOPILOT_LOG_LEVEL",
    "CRYPTOPILOT_BINANCE_REST_BASE_URL",
    "CRYPTOPILOT_BINANCE_WS_BASE_URL",
    "CRYPTOPILOT_REDIS_URL",
    "CRYPTOPILOT_REQUEST_TIMEOUT_SECONDS",
    "CRYPTOPILOT_REQUEST_MAX_RETRIES",
)


@pytest.fixture(autouse=True)
def clear_settings_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests independent from the developer machine environment."""
    for variable_name in SETTINGS_ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(variable_name, raising=False)


def load_settings() -> AppSettings:
    """Load settings without reading a local .env file."""
    return AppSettings(_env_file=None)  # type: ignore[call-arg]


def test_default_settings_are_safe() -> None:
    settings = load_settings()

    assert settings.environment is Environment.DEVELOPMENT
    assert settings.execution_mode is ExecutionMode.RESEARCH_ONLY
    assert settings.log_level == "INFO"
    assert settings.request_timeout_seconds == 10.0
    assert settings.request_max_retries == 3


def test_environment_variables_override_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRYPTOPILOT_ENVIRONMENT", "test")
    monkeypatch.setenv("CRYPTOPILOT_LOG_LEVEL", "debug")
    monkeypatch.setenv("CRYPTOPILOT_REQUEST_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("CRYPTOPILOT_REQUEST_MAX_RETRIES", "5")

    settings = load_settings()

    assert settings.environment is Environment.TEST
    assert settings.log_level == "DEBUG"
    assert settings.request_timeout_seconds == 4.5
    assert settings.request_max_retries == 5


def test_invalid_rest_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "CRYPTOPILOT_BINANCE_REST_BASE_URL",
        "this-is-not-a-valid-url",
    )

    with pytest.raises(ValidationError):
        load_settings()


@pytest.mark.parametrize("timeout", ["0", "-1"])
def test_non_positive_timeout_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    timeout: str,
) -> None:
    monkeypatch.setenv("CRYPTOPILOT_REQUEST_TIMEOUT_SECONDS", timeout)

    with pytest.raises(ValidationError):
        load_settings()


def test_unknown_execution_mode_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRYPTOPILOT_EXECUTION_MODE", "unknown-mode")

    with pytest.raises(ValidationError):
        load_settings()


@pytest.mark.parametrize(
    "mode",
    [
        "paper",
        "spot_testnet",
        "live_agentic",
    ],
)
def test_unimplemented_execution_modes_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    monkeypatch.setenv("CRYPTOPILOT_EXECUTION_MODE", mode)

    with pytest.raises(ValidationError, match="not implemented"):
        load_settings()
