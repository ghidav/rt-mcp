"""MCP tools for RT group operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_groups",
    description="List all groups in RT",
    tags={"groups", "read", "basic"},
    annotations={"title": "List RT Groups", "readOnlyHint": True},
)
async def list_groups(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List all groups."""
    try:
        await ctx.info("Fetching group list")
        groups = await client.list_groups()
        count = groups.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} groups")
        return groups
    except RTError as e:
        await ctx.error(f"Failed to list groups: {e}")
        raise


@mcp.tool(
    name="get_group",
    description="Get group details by ID or name",
    tags={"groups", "read", "basic"},
    annotations={"title": "Get RT Group", "readOnlyHint": True},
)
async def get_group(
    group_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get group details."""
    try:
        await ctx.info(f"Fetching group {group_id}")
        group = await client.get_group(group_id)
        await ctx.info(f"✓ Retrieved group {group_id}")
        return group
    except RTError as e:
        await ctx.error(f"Failed to get group {group_id}: {e}")
        raise


@mcp.tool(
    name="create_group",
    description="Create a new group",
    tags={"groups", "write", "admin"},
    annotations={"title": "Create RT Group", "readOnlyHint": False},
)
async def create_group(
    name: str,
    description: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Create a new group."""
    try:
        await ctx.info(f"Creating group '{name}'")
        group_data = {"Name": name}
        if description:
            group_data["Description"] = description

        result = await client.create_group(group_data)
        group_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created group {group_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create group: {e}")
        raise


@mcp.tool(
    name="update_group",
    description="Update an existing group",
    tags={"groups", "write", "admin"},
    annotations={"title": "Update RT Group", "readOnlyHint": False},
)
async def update_group(
    group_id: str | int,
    name: str | None = None,
    description: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Update group details."""
    try:
        await ctx.info(f"Updating group {group_id}")
        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description

        result = await client.update_group(group_id, update_data)
        await ctx.info(f"✓ Updated group {group_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update group {group_id}: {e}")
        raise


@mcp.tool(
    name="delete_group",
    description="Delete a group",
    tags={"groups", "delete", "admin"},
    annotations={"title": "Delete RT Group", "readOnlyHint": False, "destructiveHint": True},
)
async def delete_group(
    group_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Delete a group."""
    try:
        await ctx.warning(f"Deleting group {group_id}")
        result = await client.delete_group(group_id)
        await ctx.info(f"✓ Deleted group {group_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete group {group_id}: {e}")
        raise


@mcp.tool(
    name="add_group_member",
    description="Add a user to a group",
    tags={"groups", "write", "admin"},
    annotations={"title": "Add Group Member", "readOnlyHint": False},
)
async def add_group_member(
    group_id: str | int,
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Add user to group."""
    try:
        await ctx.info(f"Adding user {user_id} to group {group_id}")
        result = await client.add_group_member(group_id, user_id)
        await ctx.info(f"✓ Added user {user_id} to group {group_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to add member: {e}")
        raise


@mcp.tool(
    name="remove_group_member",
    description="Remove a user from a group",
    tags={"groups", "write", "admin"},
    annotations={"title": "Remove Group Member", "readOnlyHint": False},
)
async def remove_group_member(
    group_id: str | int,
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Remove user from group."""
    try:
        await ctx.info(f"Removing user {user_id} from group {group_id}")
        result = await client.remove_group_member(group_id, user_id)
        await ctx.info(f"✓ Removed user {user_id} from group {group_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to remove member: {e}")
        raise


@mcp.tool(
    name="search_groups",
    description="Search groups with RT query syntax",
    tags={"groups", "search", "basic"},
    annotations={"title": "Search RT Groups", "readOnlyHint": True},
)
async def search_groups(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search groups."""
    try:
        await ctx.info(f"Searching groups: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/groups", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} groups, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search groups: {e}")
        raise
