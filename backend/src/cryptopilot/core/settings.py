# 从 enum 模块导入 StrEnum：一种“字符串枚举”，成员本身就是字符串，
# 既能当枚举用（类型安全），又能直接和字符串比较/序列化。
from enum import StrEnum

# Literal：限定某个类型只能是列出的几个具体值之一（这里用于日志级别）。
# Self：表示方法返回“当前实例自身的类型”，常用于链式校验/返回 self。
from typing import Literal, Self

# Pydantic 提供的字段校验与类型工具：
#   Field          —— 为字段声明默认值及约束（如 gt/ge/le 等范围限制）
#   HttpUrl        —— 校验并规范化 HTTP/HTTPS 网址
#   RedisDsn       —— 校验 Redis 连接串（DSN）
#   WebsocketUrl   —— 校验 ws/wss 网址
#   field_validator—— 针对“单个字段”的自定义校验钩子
#   model_validator—— 针对“整个模型”的跨字段校验钩子
from pydantic import Field, HttpUrl, RedisDsn, WebsocketUrl, field_validator, model_validator

# pydantic-settings：让 Pydantic 模型能自动从环境变量 / .env 文件读取配置。
#   BaseSettings       —— 所有“配置类”的基类
#   SettingsConfigDict —— 用于声明该配置类的行为（前缀、文件、大小写等）
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported application environments.（应用支持的运行环境）"""

    # 三个环境标识，字符串值分别为 "development" / "test" / "production"。
    DEVELOPMENT = "development"  # 开发环境
    TEST = "test"  # 测试环境
    PRODUCTION = "production"  # 生产环境


class ExecutionMode(StrEnum):
    """Controls which execution capabilities may be enabled.（控制允许启用的执行能力/交易模式）"""

    # 从“只研究”到“实盘智能体”逐级放开权限的交易模式：
    RESEARCH_ONLY = "research_only"  # 仅研究（不做任何交易）
    PAPER = "paper"  # 模拟盘（虚拟资金）
    SPOT_TESTNET = "spot_testnet"  # 币安现货测试网
    LIVE_AGENTIC = "live_agentic"  # 实盘智能体（真实资金，风险最高）


# 用 type 语句定义一个“类型别名”：log_level 只能是这 5 个大写字符串之一。
# 这样写能让类型检查器（如 mypy）在编译期就发现非法日志级别。
type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class AppSettings(BaseSettings):
    """Validated application settings loaded from environment variables.

    应用的全局配置类：字段会自动从环境变量 / .env 文件读取并做类型校验。
    """

    # model_config 是 Pydantic 约定的“配置项字典”，用来控制这个类的加载行为。
    model_config = SettingsConfigDict(
        env_prefix="CRYPTOPILOT_",  # 环境变量前缀，例如 CRYPTOPILOT_LOG_LEVEL 对应 log_level
        env_file=".env",  # 从项目根目录的 .env 文件读取默认配置
        env_file_encoding="utf-8",  # .env 文件的编码
        env_ignore_empty=True,  # 环境变量为空字符串时忽略它，改用字段默认值
        case_sensitive=False,  # 环境变量名不区分大小写
        extra="ignore",  # 出现未定义的多余环境变量时直接忽略（不报错）
        frozen=True,  # 冻结实例：创建后不可修改，保证配置只读、线程安全
    )

    # ---- 基础运行参数（都带有默认值，可被环境变量覆盖）----
    environment: Environment = Environment.DEVELOPMENT  # 当前环境，默认“开发”
    execution_mode: ExecutionMode = ExecutionMode.RESEARCH_ONLY  # 执行模式，默认“仅研究”（最安全）
    log_level: LogLevel = "INFO"  # 日志级别，默认 INFO

    # ---- 外部服务地址（Pydantic 会自动校验 URL 合法性）----
    binance_rest_base_url: HttpUrl = HttpUrl(
        "https://data-api.binance.vision"
    )  # 币安 REST 接口基址
    binance_ws_base_url: WebsocketUrl = WebsocketUrl(
        "wss://data-stream.binance.vision/ws"  # 币安 WebSocket 行情流基址
    )
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")  # Redis 连接串（本地默认库 0）

    # ---- 网络请求相关约束（Field 用于附加数值范围校验）----
    # gt=0 表示必须大于 0；le=60.0 表示小于等于 60 秒。
    request_timeout_seconds: float = Field(default=10.0, gt=0, le=60.0)  # 单次请求超时时间（秒）
    # ge=0 表示大于等于 0；le=10 表示最多重试 10 次。
    request_max_retries: int = Field(default=3, ge=0, le=10)  # 请求最大重试次数

    # field_validator 针对 log_level 这一个字段做“校验前(mode='before')”的预处理。
    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        """Normalize environment-provided log levels before validation.

        在校验之前把日志级别统一转成大写，这样用户在环境变量里写 "info"、"Info"
        都能被正确识别为 "INFO"。
        """
        # 只有当传入的是字符串时才转大写；其它类型（比如已是枚举）原样返回，
        # 交给后续 Pydantic 校验逻辑处理。
        if isinstance(value, str):
            return value.upper()
        return value

    # model_validator(mode="after") 在“所有字段都校验完成后”再对整个模型做一次检查，
    # 适合做跨字段的业务规则校验。返回 Self 表示把实例原样返回。
    @model_validator(mode="after")
    def reject_unimplemented_execution_modes(self) -> Self:
        """Reject execution capabilities that are not implemented yet.

        目前项目只实现了“仅研究”模式，若用户尝试启用其它尚未实现的模式
        （模拟盘 / 测试网 / 实盘），则直接抛出错误，避免误用未完成的危险功能。
        """
        # 用 is not 做枚举身份比较；只要不是 RESEARCH_ONLY 就拦截。
        if self.execution_mode is not ExecutionMode.RESEARCH_ONLY:
            message = (
                f"Execution mode {self.execution_mode.value!r} is not implemented. "
                "Use 'research_only'."
            )
            # 抛出 ValueError，Pydantic 会将其包装成清晰的配置校验错误。
            raise ValueError(message)

        # 校验通过，返回自身（frozen=True 下不会修改任何字段）。
        return self
