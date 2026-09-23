from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from cryptopilot.domain.market import (
    Kline,
    KlineInterval,
    MarketSymbol,
    Price,
    Quantity,
)


# **overrides中**可以接受任意数量的关键字字段
# 所有传进来的关键字会收集成一个字典
# object表示类型注解表示每个值可以是任意类型
# ->表示最终返回一个Kline对象
def make_kline(**overrides: object) -> Kline:
    """Build a valid kline while allowing individual fields to be overridden."""
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    data: dict[str, object] = {
        "symbol": {
            "base_asset": "BTC",
            "quote_asset": "USDT",
        },
        "interval": KlineInterval.ONE_MINUTE,
        "open_time": open_time,
        "close_time": open_time + timedelta(minutes=1),
        "open_price": "100",
        "high_price": "110",
        "low_price": "90",
        "close_price": "105",
        "volume": "12.5",
    }
    # 用于把传入的字典值覆盖到data里面
    data.update(overrides)

    return Kline.model_validate(data)


def test_market_symbol_is_normalized() -> None:
    symbol = MarketSymbol(
        base_asset=" btc ",
        quote_asset="usdt",
    )
    # assert：在代码运行时验证你的假设，如果假设不成立就立刻报错。
    assert symbol.base_asset == "BTC"
    assert symbol.quote_asset == "USDT"
    assert symbol.value == "BTCUSDT"


# @pytest.mark.parametrize 的作用是
# 把同一份测试代码，用多组不同的参数分别执行多次，
# 而不需要为每组数据手写一个单独的测试函数。
# 首先是定义了两个形参
# 之后三串数据会按照形参方式传入下面测试案例中
@pytest.mark.parametrize(
    ("base_asset", "quote_asset"),
    [
        ("BTC!", "USDT"),
        ("BTC", "USD-T"),
        ("BTC", "BTC"),
    ],
)
def test_invalid_market_symbol_is_rejected(
    base_asset: str,
    quote_asset: str,
) -> None:
    with pytest.raises(ValidationError):
        MarketSymbol(
            base_asset=base_asset,
            quote_asset=quote_asset,
        )


# 验证 Price 使用精确的 Decimal 存储价格，避免浮点数误差
def test_price_uses_exact_decimal_value() -> None:
    price = Price.model_validate({"value": "0.1"})

    assert price.value == Decimal("0.1")
    assert isinstance(price.value, Decimal)


# 验证非正数价格（0 和负数）会被拒绝，抛出 ValidationError
@pytest.mark.parametrize("value", ["0", "-0.01"])
def test_non_positive_price_is_rejected(value: str) -> None:
    with pytest.raises(ValidationError):
        Price.model_validate({"value": value})


# 验证数量为 0 是被允许的（与价格不同，数量可以为零）
def test_zero_quantity_is_allowed() -> None:
    quantity = Quantity.model_validate({"value": "0"})

    assert quantity.value == Decimal("0")


# 验证负数数量会被拒绝，抛出 ValidationError
def test_negative_quantity_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Quantity.model_validate({"value": "-1"})


# 验证使用合法数据能成功创建 Kline，且各字段值与预期一致
def test_valid_kline_is_created() -> None:
    kline = make_kline()

    assert kline.symbol.value == "BTCUSDT"
    assert kline.interval is KlineInterval.ONE_MINUTE
    assert kline.open_price == Decimal("100")
    assert kline.close_price == Decimal("105")
    assert kline.volume == Decimal("12.5")
    assert kline.open_time.tzinfo is UTC


# 验证不带时区的朴素时间（naive datetime）会被拒绝，错误信息需包含 timezone
def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        make_kline(open_time=datetime(2026, 1, 1))


# 验证收盘时间必须晚于开盘时间，二者相等时应被拒绝
def test_close_time_must_be_later_than_open_time() -> None:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(ValidationError, match="later than"):
        make_kline(
            open_time=open_time,
            close_time=open_time,
        )


# 验证最高价不能低于开盘价，否则应被拒绝
def test_high_price_cannot_be_below_open_price() -> None:
    with pytest.raises(ValidationError, match="High price"):
        make_kline(high_price="99")


# 验证最低价不能高于收盘价，否则应被拒绝
def test_low_price_cannot_be_above_close_price() -> None:
    with pytest.raises(ValidationError, match="Low price"):
        make_kline(low_price="106")
