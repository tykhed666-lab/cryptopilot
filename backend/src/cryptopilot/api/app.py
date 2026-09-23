from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from cryptopilot import __version__
from cryptopilot.core.logging import configure_logging
from cryptopilot.core.settings import AppSettings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create the CryptoPilot API application."""

    resolved_settings = settings or AppSettings()

    configure_logging(resolved_settings.log_level)
    logger = structlog.get_logger(__name__)

    @asynccontextmanager
    async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
        """Log application startup and shutdown lifecycle events."""

        logger.info(
            "application_started",
            environment=resolved_settings.environment.value,
            execution_mode=resolved_settings.execution_mode.value,
        )

        yield

        logger.info("application_stopped")

    application = FastAPI(
        title="CryptoPilot API",
        version=__version__,
        description="Binance research and trading agent backend.",
        lifespan=lifespan,
    )

    application.state.settings = resolved_settings

    @application.get("/health/live", tags=["health"])
    async def liveness() -> dict[str, str]:
        """Report whether the API process is running."""
        return {"status": "ok"}

    return application


app = create_app()
