# 导入 FastAPI 的核心应用类。后续通过实例化 FastAPI 来创建 Web API 服务。
from fastapi import FastAPI

from cryptopilot import __version__

# creat_app是一个工厂函数，方便测试和以后注入配置


def create_app() -> FastAPI:
    """Create the CryptoPilot API application."""
    # title是api名称，version是版本号，description是api用途说明
    # 这些内容会显示在fastapi自动生成接口的文档中
    application = FastAPI(
        title="CryptoPilot API",
        version=__version__,
        description="Binance research and trading agent backend.",
    )

    # 这是一个路由装饰器，含义是：当服务器收到GET / health / live请求时，
    # 调用下面的liveness()函数。 tags = ["health"]会把这个接口归类到API文档的health分组下。
    @application.get("/health/live", tags=["health"])
    async def liveness() -> dict[str, str]:
        """Report whether the API process is running."""
        return {"status": "ok"}

    return application


app = create_app()
