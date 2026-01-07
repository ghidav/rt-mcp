"""MCP tools for RT custom role operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_custom_roles",
    description="List all custom roles in RT",
    tags={"custom-roles", "read", "admin"},
    annotations={"title": "List RT Custom Roles", "readOnlyHint": True},
)
async def list_custom_roles(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List all custom roles."""
    try:
        await ctx.info("Fetching custom roles list")
        roles = await client.list_custom_roles()
        count = roles.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} custom roles")
        return roles
    except RTError as e:
        await ctx.error(f"Failed to list custom roles: {e}")
        raise


@mcp.tool(
    name="get_custom_role",
    description="Get custom role details by ID or name",
    tags={"custom-roles", "read", "admin"},
    annotations={"title": "Get RT Custom Role", "readOnlyHint": True},
)
async def get_custom_role(
    role_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get custom role details."""
    try:
        await ctx.info(f"Fetching custom role {role_id}")
        role = await client.get_custom_role(role_id)
        await ctx.info(f"✓ Retrieved custom role {role_id}")
        return role
    except RTError as e:
        await ctx.error(f"Failed to get custom role {role_id}: {e}")
        raise


@mcp.tool(
    name="create_custom_role",
    description="Create a new custom role",
    tags={"custom-roles", "write", "admin"},
    annotations={"title": "Create RT Custom Role", "readOnlyHint": False},
)
async def create_custom_role(
    name: str,
    description: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Create a new custom role."""
    try:
        await ctx.info(f"Creating custom role '{name}'")
        role_data = {"Name": name}
        if description:
            role_data["Description"] = description

        result = await client.create_custom_role(role_data)
        role_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created custom role {role_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create custom role: {e}")
        raise


@mcp.tool(
    name="update_custom_role",
    description="Update an existing custom role",
    tags={"custom-roles", "write", "admin"},
    annotations={"title": "Update RT Custom Role", "readOnlyHint": False},
)
async def update_custom_role(
    role_id: str | int,
    name: str | None = None,
    description: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Update custom role details."""
    try:
        await ctx.info(f"Updating custom role {role_id}")
        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description

        result = await client.update_custom_role(role_id, update_data)
        await ctx.info(f"✓ Updated custom role {role_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update custom role {role_id}: {e}")
        raise


@mcp.tool(
    name="delete_custom_role",
    description="Delete a custom role",
    tags={"custom-roles", "delete", "admin"},
    annotations={"title": "Delete RT Custom Role", "readOnlyHint": False, "destructiveHint": True},
)
async def delete_custom_role(
    role_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Delete a custom role."""
    try:
        await ctx.warning(f"Deleting custom role {role_id}")
        result = await client.delete_custom_role(role_id)
        await ctx.info(f"✓ Deleted custom role {role_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete custom role {role_id}: {e}")
        raise


@mcp.tool(
    name="search_custom_roles",
    description="Search custom roles with RT query syntax",
    tags={"custom-roles", "search", "admin"},
    annotations={"title": "Search RT Custom Roles", "readOnlyHint": True},
)
async def search_custom_roles(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search custom roles."""
    try:
        await ctx.info(f"Searching custom roles: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/customroles", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} custom roles, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search custom roles: {e}")
        raise
