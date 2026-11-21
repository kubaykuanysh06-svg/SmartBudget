"""ARQ worker settings and background task definitions."""

from __future__ import annotations

import logging
from arq.connections import RedisSettings
from src.core.config import settings

logger = logging.getLogger(__name__)


async def check_price_drops(ctx: dict) -> None:
    """Periodic task to check price changes and notify users."""
    logger.info("Executing price drops check task...")


async def refresh_deals(ctx: dict) -> None:
    """Periodic task to refresh deals and discounts."""
    logger.info("Executing refresh deals task...")


async def startup(ctx: dict) -> None:
    logger.info("ARQ worker started.")


async def shutdown(ctx: dict) -> None:
    logger.info("ARQ worker shutting down.")


class WorkerSettings:
    """ARQ Worker configuration."""

    functions = [check_price_drops, refresh_deals]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
