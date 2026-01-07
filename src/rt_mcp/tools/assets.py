"""MCP tools for RT asset operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_assets",
    description="List all assets in RT",
    tags={"assets", "read", "basic"},
    annotations={"title": "List RT Assets", "readOnlyHint": True},
)
async def list_assets(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List all assets."""
    try:
        await ctx.info("Fetching asset list")
        assets = await client.list_assets()
        count = assets.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} assets")
        return assets
    except RTError as e:
        await ctx.error(f"Failed to list assets: {e}")
        raise


@mcp.tool(
    name="get_asset",
    description="Get asset details by ID",
    tags={"assets", "read", "basic"},
    annotations={"title": "Get RT Asset", "readOnlyHint": True},
)
async def get_asset(
    asset_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get asset details."""
    try:
        await ctx.info(f"Fetching asset {asset_id}")
        asset = await client.get_asset(asset_id)
        await ctx.info(f"✓ Retrieved asset {asset_id}")
        return asset
    except RTError as e:
        await ctx.error(f"Failed to get asset {asset_id}: {e}")
        raise


@mcp.tool(
    name="create_asset",
    description="Create a new asset",
    tags={"assets", "write", "basic"},
    annotations={"title": "Create RT Asset", "readOnlyHint": False},
)
async def create_asset(
    name: str,
    catalog: str,
    description: str | None = None,
    status: str = "allocated",
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Create a new asset."""
    try:
        await ctx.info(f"Creating asset '{name}'")
        asset_data = {"Name": name, "Catalog": catalog, "Status": status}
        if description:
            asset_data["Description"] = description

        result = await client.create_asset(asset_data)
        asset_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created asset {asset_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create asset: {e}")
        raise


@mcp.tool(
    name="update_asset",
    description="Update an existing asset",
    tags={"assets", "write", "basic"},
    annotations={"title": "Update RT Asset", "readOnlyHint": False},
)
async def update_asset(
    asset_id: int,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Update asset details."""
    try:
        await ctx.info(f"Updating asset {asset_id}")
        update_data = {}
        if name:
            update_data["Name"] = name
        if description:
            update_data["Description"] = description
        if status:
            update_data["Status"] = status

        result = await client.update_asset(asset_id, update_data)
        await ctx.info(f"✓ Updated asset {asset_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update asset {asset_id}: {e}")
        raise


@mcp.tool(
    name="delete_asset",
    description="Delete an asset",
    tags={"assets", "delete", "admin"},
    annotations={"title": "Delete RT Asset", "readOnlyHint": False, "destructiveHint": True},
)
async def delete_asset(
    asset_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Delete an asset."""
    try:
        await ctx.warning(f"Deleting asset {asset_id}")
        result = await client.delete_asset(asset_id)
        await ctx.info(f"✓ Deleted asset {asset_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete asset {asset_id}: {e}")
        raise


@mcp.tool(
    name="search_assets",
    description="Search assets with RT query syntax",
    tags={"assets", "search", "basic"},
    annotations={"title": "Search RT Assets", "readOnlyHint": True},
)
async def search_assets(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search assets."""
    try:
        await ctx.info(f"Searching assets: {query}")
        results = await client.search_assets(query, page, per_page)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} assets, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search assets: {e}")
        raise
