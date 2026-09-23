from decimal import Decimal


# 项目的顶层异常基类，继承自 Python 内置的 Exception。所有"项目预期内的错误"都从它派生。
# 这样在代码里可以用 except CryptoPilotError 一次性捕获本项目的所有异常。
class CryptoPilotError(Exception):
    """Base exception for expected CryptoPilot failures."""


# 业务规则（领域层）错误的基类 ，只是继承关系的一个分类节点
class DomainError(CryptoPilotError):
    """Base exception for business-rule failures."""


# 交易安全错误的基类，继承自 DomainError。表示确定性的交易安全拒绝。
class TradingSafetyError(DomainError):
    """Base exception for deterministic trading-safety rejections."""


# 交易禁用错误，继承自 TradingSafetyError。表示在当前执行模式下不允许提交订单。
class TradingDisabledError(TradingSafetyError):
    """Raised when an execution mode does not permit order submission."""

    def __init__(self, execution_mode: str) -> None:
        self.execution_mode = execution_mode
        message = f"Order submission is disabled in execution mode {execution_mode!r}"
        # super().__init__(message) 把消息传给父类，让异常能正常显示
        super().__init__(message)


class RiskLimitExceededError(TradingSafetyError):
    """Raised when a proposed order exceeds a deterministic risk limit."""

    # 参数列表里的 * 表示后面的 rule、observed_value、allowed_value
    # 都必须用关键字方式传入（如 rule="max_notional"）
    def __init__(
        self,
        *,
        rule: str,
        observed_value: Decimal,
        allowed_value: Decimal,
    ) -> None:
        self.rule = rule
        self.observed_value = observed_value
        self.allowed_value = allowed_value

        message = (
            f"Risk rule {rule!r} rejected the operation: "
            f"observed={observed_value}, allowed={allowed_value}"
        )
        super().__init__(message)
