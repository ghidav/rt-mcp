"""MCP tools for RT catalog operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_catalogs",
    description="List all catalogs in RT",
    tags={"catalogs", "read", "basic"},
    annotations={"title": "List RT Catalogs", "readOnlyHint": True},
)
async def list_catalogs(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List all catalogs."""
    try:
        await ctx.info("Fetching catalog list")
        catalogs = await client.list_catalogs()
        count = catalogs.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} catalogs")
        return catalogs
    except RTError as e:
        await ctx.error(f"Failed to list catalogs: {e}")
        raise


@mcp.tool(
    name="get_catalog",
    description="Get catalog details by ID or name",
    tags={"catalogs", "read", "basic"},
    annotations={"title": "Get RT Catalog", "readOnlyHint": True},
)
async def get_catalog(
    catalog_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get catalog details."""
    try:
        await ctx.info(f"Fetching catalog {catalog_id}")
        catalog = await client.get_catalog(catalog_id)
        await ctx.info(f"✓ Retrieved catalog {catalog_id}")
        return catalog
    except RTError as e:
        await ctx.error(f"Failed to get catalog {catalog_id}: {e}")
        raise


@mcp.tool(
    name="create_catalog",
    description="Create a new catalog",
    tags={"catalogs", "write", "admin"},
    annotations={"title": "Create RT Catalog", "readOnlyHint": False},
)
async def create_catalog(
    name: str,
    description: str | None = None,
    disabled: bool = False,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Create a new catalog."""
    try:
        await ctx.info(f"Creating catalog '{name}'")
        catalog_data = {"Name": name, "Disabled": 1 if disabled else 0}
        if description:
            catalog_data["Description"] = description

        result = await client.create_catalog(catalog_data)
        catalog_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created catalog {catalog_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create catalog: {e}")
        raise


@mcp.tool(
    name="update_catalog",
    description="Update an existing catalog",
    tags={"catalogs", "write", "admin"},
    annotations={"title": "Update RT Catalog", "readOnlyHint": False},
)
async def update_catalog(
    catalog_id: str | int,
    name: str | None = None,
    description: str | None = None,
    disabled: bool | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Update catalog details."""
    try:
        await ctx.info(f"Updating catalog {catalog_id}")
        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description
        if disabled is not None:
            update_data["Disabled"] = 1 if disabled else 0

        result = await client.update_catalog(catalog_id, update_data)
        await ctx.info(f"✓ Updated catalog {catalog_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update catalog {catalog_id}: {e}")
        raise


@mcp.tool(
    name="delete_catalog",
    description="Delete a catalog",
    tags={"catalogs", "delete", "admin"},
    annotations={"title": "Delete RT Catalog", "readOnlyHint": False, "destructiveHint": True},
)
async def delete_catalog(
    catalog_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Delete a catalog."""
    try:
        await ctx.warning(f"Deleting catalog {catalog_id}")
        result = await client.delete_catalog(catalog_id)
        await ctx.info(f"✓ Deleted catalog {catalog_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete catalog {catalog_id}: {e}")
        raise


@mcp.tool(
    name="search_catalogs",
    description="Search catalogs with RT query syntax",
    tags={"catalogs", "search", "basic"},
    annotations={"title": "Search RT Catalogs", "readOnlyHint": True},
)
async def search_catalogs(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search catalogs."""
    try:
        await ctx.info(f"Searching catalogs: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/catalogs", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} catalogs, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search catalogs: {e}")
        raise
