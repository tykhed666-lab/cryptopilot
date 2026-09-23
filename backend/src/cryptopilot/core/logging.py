import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

# 敏感值被屏蔽后统一替换成的占位符
REDACTED_VALUE = "[REDACTED]"

# 需要精确匹配的敏感字段名集合，用 frozenset 保证查找快且不可修改
SENSITIVE_FIELD_NAMES = frozenset(
    {
        "api_key",
        "api_secret",
        "secret_key",
        "authorization",
        "password",
        "passphrase",
        "access_token",
        "refresh_token",
    }
)

# 需要按后缀匹配的敏感字段，用于捕捉带前缀的字段名（如 binance_api_key）
SENSITIVE_FIELD_SUFFIXES = (
    "_api_key",
    "_api_secret",
    "_password",
    "_passphrase",
    "_token",
)


# 判断某个日志字段名是否可能包含敏感信息
def _is_sensitive_field(field_name: str) -> bool:
    """Return whether a structured log field may contain a secret."""
    # 归一化后的字段名：去空格、转小写、把 - 换成 _，以便统一比对
    normalized_name = field_name.strip().lower().replace("-", "_")

    return normalized_name in SENSITIVE_FIELD_NAMES or normalized_name.endswith(
        SENSITIVE_FIELD_SUFFIXES
    )


# 递归屏蔽嵌套容器（dict / list / tuple）中的敏感值
def _redact_value(value: Any) -> Any:
    """Recursively redact sensitive values in nested containers."""
    if isinstance(value, dict):
        return {
            key: (
                REDACTED_VALUE
                if isinstance(key, str) and _is_sensitive_field(key)
                else _redact_value(nested_value)
            )
            for key, nested_value in value.items()
        }

    if isinstance(value, list):
        return [_redact_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)

    return value


# structlog 处理器：在日志事件被渲染前屏蔽掉其中的敏感数据
def redact_sensitive_data(
    _logger: WrappedLogger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Redact secrets before a structured event is rendered."""
    # 这是字典推导式，用于遍历原始字典中的键值对
    # 并返回一个新的字典，其中包含屏蔽敏感数据后的结果
    return {
        key: (REDACTED_VALUE if _is_sensitive_field(key) else _redact_value(value))
        for key, value in event_dict.items()
    }


# 日志配置入口：设置标准库 logging，并配置 structlog 的 JSON 输出流水线
def configure_logging(log_level: str = "INFO") -> None:
    """Configure standard logging and structlog JSON output."""
    logging.basicConfig(
        format="%(message)s",
        level=log_level.upper(),
        stream=sys.stdout,
        force=True,
    )

    structlog.configure(
        # processors 是一条日志处理流水线，事件会按顺序依次经过每个处理器
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            redact_sensitive_data,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
