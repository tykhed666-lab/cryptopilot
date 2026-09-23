from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# KlineInterval 表示 K 线时间周期，例如 1m、1h、1d。
# 字符串枚举可以直接参与 JSON 序列化，
# 也方便与交易所 API 的参数保持一致。
class KlineInterval(StrEnum):
    """Kline intervals currently supported by CryptoPilot."""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


# 标准化交易对模型
class MarketSymbol(BaseModel):
    """A normalized Binance spot-market trading pair."""

    # frozen=true，对象创建后不可修改
    model_config = ConfigDict(frozen=True)
    # 定义了交易对的两个属性：base_asset 和 quote_asset，
    # 分别表示交易对的基础资产和报价资产。
    # 这两个属性都继承自 str，并且都添加了字段验证器，
    # 确保它们只包含字母和数字，并且长度在 1 到 20 个字符之间。
    base_asset: str = Field(min_length=1, max_length=20)
    quote_asset: str = Field(min_length=1, max_length=20)

    # field_validator 装饰器用于在模型验证之前对字段进行预处理
    @field_validator("base_asset", "quote_asset", mode="before")
    # classmethod是类方法，正常需要对象调用类里面的方法，而类方法可以直接通过类来电泳
    @classmethod
    # 定义了两个类方法：normalize_asset 和 validate_asset。normalize_asset 方法
    # 用于将资产代码转换为大写形式，并去除前后的空格。
    def normalize_asset(cls, value: object) -> object:
        """Normalize asset codes such as btc and usdt."""
        if isinstance(value, str):
            return value.strip().upper()
        return value

    # 验证资产代码是否只包含字母和数字，并且长度在 1 到 20 个字符之间。
    # 确保它们只包含字母和数字，并且长度在 1 到 20 个字符之间。
    @field_validator("base_asset", "quote_asset")
    @classmethod
    def validate_asset(cls, value: str) -> str:
        """Allow only letters and digits in Binance asset codes."""
        if not value.isalnum():
            raise ValueError("Asset code must contain only letters and digits")
        return value

    # 模型验证器，在模型验证之后执行，用于拒绝基础资产和报价资产相同的交易对。
    @model_validator(mode="after")
    def reject_identical_assets(self) -> Self:
        """A trading pair must contain two different assets."""
        if self.base_asset == self.quote_asset:
            raise ValueError("Base asset and quote asset must be different")
        return self

    # 属性装饰器，用于返回交易对的字符串表示，即基础资产和报价资产的拼接。
    # 用于拼接出满足币安api要求的字符
    @property
    def value(self) -> str:
        """Return the Binance symbol representation."""
        return f"{self.base_asset}{self.quote_asset}"


class Price(BaseModel):
    """A strictly positive monetary price."""

    # 把实例设为只读不可变
    model_config = ConfigDict(frozen=True)
    # 定义了一个属性 value，表示价格的 Decimal 值，并添加了一个字段验证器，确保价格严格大于 0。
    # decimal规定十进制，gt=0表示大于0
    value: Decimal = Field(gt=0)


class Quantity(BaseModel):
    """A non-negative asset quantity."""

    # 把实例设为只读不可变
    model_config = ConfigDict(frozen=True)
    # 定义了一个属性 value，表示数量的 Decimal 值，并添加了一个字段验证器，确保数量大于或等于 0。
    value: Decimal = Field(ge=0)


class Kline(BaseModel):
    """An immutable OHLCV market-data candle."""

    model_config = ConfigDict(frozen=True)

    symbol: MarketSymbol
    interval: KlineInterval
    open_time: datetime
    close_time: datetime
    open_price: Decimal = Field(gt=0)
    high_price: Decimal = Field(gt=0)
    low_price: Decimal = Field(gt=0)
    close_price: Decimal = Field(gt=0)
    volume: Decimal = Field(ge=0)

    # 时区感知（require_timezone）：强制拒绝不带时区信息的 Naive Datetime，
    # 并将所有时间统一转换为 UTC，防止跨时区交易逻辑产生时间错乱。
    @field_validator("open_time", "close_time")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Reject ambiguous datetimes and normalize valid values to UTC."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_market_boundaries(self) -> Self:
        """Validate the temporal and price boundaries of the candle."""
        if self.close_time <= self.open_time:
            raise ValueError("Close time must be later than open time")

        if self.high_price < max(self.open_price, self.close_price):
            raise ValueError("High price cannot be below open or close price")

        if self.low_price > min(self.open_price, self.close_price):
            raise ValueError("Low price cannot be above open or close price")

        if self.high_price < self.low_price:
            raise ValueError("High price cannot be below low price")

        return self
