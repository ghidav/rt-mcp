"""MCP tools for RT queue operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_queues",
    description="List all queues in RT",
    tags={"queues", "read", "basic"},
    annotations={
        "title": "List RT Queues",
        "readOnlyHint": True,
    },
)
async def list_queues(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    List all queues.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        List of queues
    """
    try:
        await ctx.info("Fetching queue list")
        queues = await client.list_queues()
        count = queues.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} queues")
        return queues
    except RTError as e:
        await ctx.error(f"Failed to list queues: {e}")
        raise


@mcp.tool(
    name="get_queue",
    description="Get queue details by ID or name",
    tags={"queues", "read", "basic"},
    annotations={
        "title": "Get RT Queue",
        "readOnlyHint": True,
    },
)
async def get_queue(
    queue_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get queue details by ID or name.

    Args:
        queue_id: Queue ID or name
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Queue details
    """
    try:
        await ctx.info(f"Fetching queue {queue_id}")
        queue = await client.get_queue(queue_id)
        await ctx.info(f"✓ Retrieved queue {queue_id}")
        return queue
    except RTError as e:
        await ctx.error(f"Failed to get queue {queue_id}: {e}")
        raise


@mcp.tool(
    name="create_queue",
    description="Create a new queue",
    tags={"queues", "write", "admin"},
    annotations={
        "title": "Create RT Queue",
        "readOnlyHint": False,
    },
)
async def create_queue(
    name: str,
    description: str | None = None,
    correspond_address: str | None = None,
    comment_address: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Create a new queue.

    Args:
        name: Queue name
        description: Queue description
        correspond_address: Email address for correspondence
        comment_address: Email address for comments
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Created queue data
    """
    try:
        await ctx.info(f"Creating queue '{name}'")

        queue_data = {"Name": name}
        if description:
            queue_data["Description"] = description
        if correspond_address:
            queue_data["CorrespondAddress"] = correspond_address
        if comment_address:
            queue_data["CommentAddress"] = comment_address

        result = await client.create_queue(queue_data)
        queue_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created queue {queue_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create queue: {e}")
        raise


@mcp.tool(
    name="update_queue",
    description="Update an existing queue",
    tags={"queues", "write", "admin"},
    annotations={
        "title": "Update RT Queue",
        "readOnlyHint": False,
    },
)
async def update_queue(
    queue_id: str | int,
    name: str | None = None,
    description: str | None = None,
    correspond_address: str | None = None,
    comment_address: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Update queue details.

    Args:
        queue_id: Queue ID or name
        name: New queue name
        description: New description
        correspond_address: New correspondence email
        comment_address: New comment email
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Updated queue data
    """
    try:
        await ctx.info(f"Updating queue {queue_id}")

        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description
        if correspond_address:
            update_data["CorrespondAddress"] = correspond_address
        if comment_address:
            update_data["CommentAddress"] = comment_address

        result = await client.update_queue(queue_id, update_data)
        await ctx.info(f"✓ Updated queue {queue_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update queue {queue_id}: {e}")
        raise


@mcp.tool(
    name="search_queues",
    description="Search queues with RT query syntax",
    tags={"queues", "search", "basic"},
    annotations={
        "title": "Search RT Queues",
        "readOnlyHint": True,
    },
)
async def search_queues(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Search queues using RT query syntax.

    Args:
        query: RT query string (e.g., "Name LIKE 'Support%'")
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Paginated search results
    """
    try:
        await ctx.info(f"Searching queues: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/queues", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} queues, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search queues: {e}")
        raise


@mcp.tool(
    name="disable_queue",
    description="Disable a queue",
    tags={"queues", "write", "admin"},
    annotations={
        "title": "Disable RT Queue",
        "readOnlyHint": False,
        "destructiveHint": True,
    },
)
async def disable_queue(
    queue_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Disable a queue.

    Args:
        queue_id: Queue ID or name
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of disable operation
    """
    try:
        await ctx.warning(f"Disabling queue {queue_id}")
        result = await client.update_queue(queue_id, {"Disabled": 1})
        await ctx.info(f"✓ Disabled queue {queue_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to disable queue {queue_id}: {e}")
        raise


@mcp.tool(
    name="enable_queue",
    description="Enable a disabled queue",
    tags={"queues", "write", "admin"},
    annotations={
        "title": "Enable RT Queue",
        "readOnlyHint": False,
    },
)
async def enable_queue(
    queue_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Enable a disabled queue.

    Args:
        queue_id: Queue ID or name
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of enable operation
    """
    try:
        await ctx.info(f"Enabling queue {queue_id}")
        result = await client.update_queue(queue_id, {"Disabled": 0})
        await ctx.info(f"✓ Enabled queue {queue_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to enable queue {queue_id}: {e}")
        raise
