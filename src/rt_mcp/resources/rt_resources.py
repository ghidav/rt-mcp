"""MCP resources for RT reference data."""

import json
from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.resource("rt://queues/list")
async def get_queues_resource(
    ctx: Context,
    client: RTClient = Depends(get_rt_client),
) -> str:
    """
    List all RT queues as a resource.

    This provides quick access to available queues for reference.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        JSON string of queues
    """
    try:
        await ctx.info("Fetching queues resource")
        queues = await client.list_queues()
        return json.dumps(queues, indent=2)
    except RTError as e:
        await ctx.error(f"Failed to fetch queues resource: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("rt://custom-fields/list")
async def get_custom_fields_resource(
    ctx: Context,
    client: RTClient = Depends(get_rt_client),
) -> str:
    """
    List all custom fields as a resource.

    This provides quick access to available custom fields for reference.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        JSON string of custom fields
    """
    try:
        await ctx.info("Fetching custom fields resource")
        fields = await client.list_custom_fields()
        return json.dumps(fields, indent=2)
    except RTError as e:
        await ctx.error(f"Failed to fetch custom fields resource: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("rt://user/current")
async def get_current_user_resource(
    ctx: Context,
    client: RTClient = Depends(get_rt_client),
) -> str:
    """
    Get current authenticated user as a resource.

    This provides quick access to current user information.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        JSON string of current user
    """
    try:
        await ctx.info("Fetching current user resource")
        user = await client.get_current_user()
        return json.dumps(user, indent=2)
    except RTError as e:
        await ctx.error(f"Failed to fetch current user resource: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("rt://server/info")
async def get_server_info_resource(
    ctx: Context,
    client: RTClient = Depends(get_rt_client),
) -> str:
    """
    Get RT server information as a resource.

    This provides quick access to server configuration and version.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        JSON string of server info
    """
    try:
        await ctx.info("Fetching server info resource")
        info = await client._request("GET", "/")
        return json.dumps(info, indent=2)
    except RTError as e:
        await ctx.error(f"Failed to fetch server info resource: {e}")
        return json.dumps({"error": str(e)})
