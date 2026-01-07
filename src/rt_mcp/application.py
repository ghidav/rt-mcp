"""RT MCP Application - Central MCP instance definition."""

import sys
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from .config import RTConfig
from .client import RTClient


@asynccontextmanager
async def lifespan(mcp):
    """
    Server lifecycle management.

    Handles startup validation and graceful shutdown.
    """
    # Startup
    try:
        config = RTConfig()
        print("🚀 RT MCP Server starting", file=sys.stderr)
        print(f"   RT URL: {config.rt_url}", file=sys.stderr)
        print(f"   Auth: {'Token' if config.rt_token else 'Basic'}", file=sys.stderr)
        print(f"   SSL Verify: {config.rt_verify_ssl}", file=sys.stderr)

        # Optional: Try to validate connection (non-fatal)
        try:
            async with RTClient(config) as client:
                await client.validate_connection()
            print("✓ RT connection validated", file=sys.stderr)
        except Exception as e:
            print(f"⚠ RT connection not available: {e}", file=sys.stderr)
            print("  Server will start anyway - tools will fail if RT is unreachable", file=sys.stderr)

        print("✓ RT MCP Server ready", file=sys.stderr)
    except Exception as e:
        print(f"✗ Failed to start server: {e}", file=sys.stderr)
        raise

    yield

    # Shutdown
    print("👋 RT MCP Server shutdown", file=sys.stderr)


# Initialize FastMCP server
mcp = FastMCP(
    name="rt-mcp-server",
    version="0.1.0",
    instructions="""
    Request Tracker (RT) REST2 API MCP Server

    Provides comprehensive access to RT via 85+ tools organized by tags.

    🎯 Filter by resource type:
    tickets, queues, users, groups, assets, catalogs, transactions,
    attachments, custom-fields, custom-roles

    🔧 Filter by operation:
    read (safe), write (state-changing), delete (destructive), search

    👤 Filter by permission level:
    basic, power-user, admin

    Authentication configured via RT_URL, RT_TOKEN (or RT_USER/RT_PASSWORD).
    """,
    lifespan=lifespan,
)
