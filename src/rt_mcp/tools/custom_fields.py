"""MCP tools for RT custom field operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_custom_fields",
    description="List all custom fields in RT",
    tags={"custom-fields", "read", "basic"},
    annotations={"title": "List RT Custom Fields", "readOnlyHint": True},
)
async def list_custom_fields(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List all custom fields."""
    try:
        await ctx.info("Fetching custom fields list")
        fields = await client.list_custom_fields()
        count = fields.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} custom fields")
        return fields
    except RTError as e:
        await ctx.error(f"Failed to list custom fields: {e}")
        raise


@mcp.tool(
    name="get_custom_field",
    description="Get custom field details by ID or name",
    tags={"custom-fields", "read", "basic"},
    annotations={"title": "Get RT Custom Field", "readOnlyHint": True},
)
async def get_custom_field(
    field_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get custom field details."""
    try:
        await ctx.info(f"Fetching custom field {field_id}")
        field = await client.get_custom_field(field_id)
        await ctx.info(f"✓ Retrieved custom field {field_id}")
        return field
    except RTError as e:
        await ctx.error(f"Failed to get custom field {field_id}: {e}")
        raise


@mcp.tool(
    name="create_custom_field",
    description="Create a new custom field",
    tags={"custom-fields", "write", "admin"},
    annotations={"title": "Create RT Custom Field", "readOnlyHint": False},
)
async def create_custom_field(
    name: str,
    type: str,
    description: str | None = None,
    lookup_type: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Create a new custom field."""
    try:
        await ctx.info(f"Creating custom field '{name}'")
        field_data = {"Name": name, "Type": type}
        if description:
            field_data["Description"] = description
        if lookup_type:
            field_data["LookupType"] = lookup_type

        result = await client.create_custom_field(field_data)
        field_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created custom field {field_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create custom field: {e}")
        raise


@mcp.tool(
    name="update_custom_field",
    description="Update an existing custom field",
    tags={"custom-fields", "write", "admin"},
    annotations={"title": "Update RT Custom Field", "readOnlyHint": False},
)
async def update_custom_field(
    field_id: str | int,
    name: str | None = None,
    description: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Update custom field details."""
    try:
        await ctx.info(f"Updating custom field {field_id}")
        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description

        result = await client.update_custom_field(field_id, update_data)
        await ctx.info(f"✓ Updated custom field {field_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update custom field {field_id}: {e}")
        raise


@mcp.tool(
    name="delete_custom_field",
    description="Delete a custom field",
    tags={"custom-fields", "delete", "admin"},
    annotations={"title": "Delete RT Custom Field", "readOnlyHint": False, "destructiveHint": True},
)
async def delete_custom_field(
    field_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Delete a custom field."""
    try:
        await ctx.warning(f"Deleting custom field {field_id}")
        result = await client.delete_custom_field(field_id)
        await ctx.info(f"✓ Deleted custom field {field_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete custom field {field_id}: {e}")
        raise


@mcp.tool(
    name="search_custom_fields",
    description="Search custom fields with RT query syntax",
    tags={"custom-fields", "search", "basic"},
    annotations={"title": "Search RT Custom Fields", "readOnlyHint": True},
)
async def search_custom_fields(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search custom fields."""
    try:
        await ctx.info(f"Searching custom fields: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/customfields", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} custom fields, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search custom fields: {e}")
        raise
