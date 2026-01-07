"""Dependency injection providers for RT MCP server."""

from contextlib import asynccontextmanager
from .client import RTClient
from .config import RTConfig

# Global client instance
_rt_client: RTClient | None = None


def get_config() -> RTConfig:
    """
    Get RT configuration from environment variables.

    Returns:
        RT configuration instance
    """
    return RTConfig()


@asynccontextmanager
async def get_rt_client():
    """
    Get or create RT client instance with lifecycle management.

    This dependency is injected into tools and provides an async context
    manager that ensures the HTTP client is properly initialized and cleaned up.

    Yields:
        RT client instance
    """
    global _rt_client
    if _rt_client is None:
        config = get_config()
        _rt_client = RTClient(config)

    async with _rt_client as client:
        yield client
