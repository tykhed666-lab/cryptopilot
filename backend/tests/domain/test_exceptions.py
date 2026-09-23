from decimal import Decimal

import pytest

from cryptopilot.domain.exceptions import (
    CryptoPilotError,
    DomainError,
    RiskLimitExceededError,
    TradingDisabledError,
    TradingSafetyError,
)


def test_trading_disabled_error_contains_execution_mode() -> None:
    error = TradingDisabledError("research_only")

    assert error.execution_mode == "research_only"
    assert "research_only" in str(error)


def test_risk_limit_error_contains_structured_context() -> None:
    error = RiskLimitExceededError(
        rule="maximum_order_notional",
        observed_value=Decimal("1250"),
        allowed_value=Decimal("1000"),
    )

    assert error.rule == "maximum_order_notional"
    assert error.observed_value == Decimal("1250")
    assert error.allowed_value == Decimal("1000")
    assert "observed=1250" in str(error)
    assert "allowed=1000" in str(error)


@pytest.mark.parametrize(
    "error",
    [
        TradingDisabledError("research_only"),
        RiskLimitExceededError(
            rule="maximum_position_size",
            observed_value=Decimal("2"),
            allowed_value=Decimal("1"),
        ),
    ],
)
def test_safety_errors_share_a_common_base(
    error: TradingSafetyError,
) -> None:
    assert isinstance(error, TradingSafetyError)
    assert isinstance(error, DomainError)
    assert isinstance(error, CryptoPilotError)
    assert isinstance(error, Exception)
