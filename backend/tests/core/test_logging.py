# json 用于解析日志最终输出的 JSON 字符串（端到端测试时使用）
import json

# pytest 提供测试框架能力，这里用到它的 capsys 夹具捕获标准输出
import pytest

# structlog 是项目使用的结构化日志库，测试中用它来产生日志事件
import structlog

# capture_logs 是 structlog 提供的测试工具：
# 它会临时接管日志流水线，把日志事件以字典形式收集起来，
# 方便我们直接断言字段的值，而不用去解析文本输出
from structlog.testing import capture_logs

# 导入被测模块（cryptopilot.core.logging）中的三个公开对象：
# - REDACTED_VALUE：敏感值被屏蔽后统一替换成的占位符 "[REDACTED]"
# - configure_logging：日志配置入口，设置 structlog 的 JSON 输出流水线
# - redact_sensitive_data：structlog 处理器，负责在渲染前屏蔽敏感数据
from cryptopilot.core.logging import (
    REDACTED_VALUE,
    configure_logging,
    redact_sensitive_data,
)


# 测试：顶层敏感字段是否会被屏蔽
def test_top_level_sensitive_fields_are_redacted() -> None:
    # capture_logs 上下文管理器只挂载 redact_sensitive_data 这一个处理器，
    # 从而隔离地测试脱敏逻辑本身，不受时间戳、JSON 渲染等其他处理器干扰
    with capture_logs(processors=[redact_sensitive_data]) as logs:
        # 产生一条带敏感字段（api_key / api_secret）和普通字段（symbol）的日志
        structlog.get_logger().info(
            "binance_request",
            api_key="api-key-value",
            api_secret="api-secret-value",
            symbol="BTCUSDT",
        )

    # logs 是收集到的事件字典列表，这里只记录了一条日志
    event = logs[0]

    # 敏感字段的值应被替换为统一的占位符
    assert event["api_key"] == REDACTED_VALUE
    assert event["api_secret"] == REDACTED_VALUE
    # 非敏感字段应保持原值不变
    assert event["symbol"] == "BTCUSDT"


# 测试：嵌套结构（dict 套 dict、list 套 dict）中的敏感字段是否也会被屏蔽
def test_nested_sensitive_fields_are_redacted() -> None:
    with capture_logs(processors=[redact_sensitive_data]) as logs:
        # account 是多层嵌套字典，requests 是包含字典的列表，
        # 用于验证脱敏逻辑能递归处理任意深度的容器
        structlog.get_logger().info(
            "account_loaded",
            account={
                # password 是精确匹配的敏感字段名
                "password": "password-value",
                "profile": {
                    # access_token 位于第二层嵌套中，同样应被识别并屏蔽
                    "access_token": "token-value",
                    "mode": "research_only",
                },
            },
            requests=[
                {
                    "authorization": "authorization-value",
                    "symbol": "ETHUSDT",
                }
            ],
        )

    event = logs[0]
    account = event["account"]
    requests = event["requests"]

    # 第一层嵌套的敏感字段被屏蔽
    assert account["password"] == REDACTED_VALUE
    # 第二层嵌套的敏感字段同样被屏蔽（递归生效）
    assert account["profile"]["access_token"] == REDACTED_VALUE
    # 嵌套中的非敏感字段保持原值
    assert account["profile"]["mode"] == "research_only"
    # 列表元素（字典）内的敏感字段也会被屏蔽
    assert requests[0]["authorization"] == REDACTED_VALUE
    assert requests[0]["symbol"] == "ETHUSDT"


# 测试：不同书写风格的敏感字段名（大小写、连字符、前缀）能否被归一化识别
def test_sensitive_field_names_are_normalized() -> None:
    with capture_logs(processors=[redact_sensitive_data]) as logs:
        # 因为 "API-Key"、"BINANCE_API_SECRET" 不是合法的 Python 标识符，
        # 无法直接作为关键字参数传入，所以用 **{...} 字典解包的方式传递
        structlog.get_logger().info(
            "credentials_checked",
            **{
                # "API-Key"：包含大写和连字符，归一化后应变为 "api_key"（精确匹配）
                "API-Key": "first-secret",
                # "BINANCE_API_SECRET"：带前缀的大写字段，
                # 归一化后应以 "_api_secret" 结尾（后缀匹配）
                "BINANCE_API_SECRET": "second-secret",
            },
        )

    event = logs[0]

    # 两种非标准写法都应命中敏感字段规则并被屏蔽
    assert event["API-Key"] == REDACTED_VALUE
    assert event["BINANCE_API_SECRET"] == REDACTED_VALUE


# 测试：端到端验证——调用 configure_logging 后，真实输出是否为脱敏过的 JSON
# capsys 是 pytest 内置夹具，用于捕获 print / logging 写到 stdout 的内容
def test_configured_logging_emits_redacted_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # 按生产环境的方式配置日志流水线（含脱敏处理器和 JSON 渲染器）
    configure_logging("INFO")

    # 通过具名 logger 产生一条混合了普通字段和敏感字段的日志
    structlog.get_logger("test_logger").info(
        "binance_connected",
        symbol="BTCUSDT",
        api_key="must-not-leak",
    )

    # 读取被捕获的标准输出，并去掉首尾空白（日志末尾带换行符）
    output = capsys.readouterr().out.strip()
    # 输出应当是一行合法的 JSON，可直接反序列化为字典
    event = json.loads(output)

    # 验证流水线中各处理器添加的标准字段是否符合预期
    assert event["event"] == "binance_connected"  # 日志事件名
    assert event["logger"] == "test_logger"  # 由 add_logger_name 处理器添加
    assert event["level"] == "info"  # 由 add_log_level 处理器添加
    assert event["symbol"] == "BTCUSDT"  # 非敏感字段保持原值
    assert event["api_key"] == REDACTED_VALUE  # 敏感字段被屏蔽
    assert "timestamp" in event  # 由 TimeStamper 处理器添加
    # 兜底断言：敏感值明文绝不能出现在最终输出中
    assert "must-not-leak" not in output
