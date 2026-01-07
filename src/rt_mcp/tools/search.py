"""MCP tools for advanced RT search operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="search_all",
    description="Search across all RT object types (tickets, queues, users, assets, etc.)",
    tags={"search", "read", "power-user"},
    annotations={"title": "Global RT Search", "readOnlyHint": True},
)
async def search_all(
    query: str,
    object_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Search across all RT objects.

    Args:
        query: RT query string
        object_type: Optional object type filter (ticket, queue, user, asset, etc.)
        page: Page number
        per_page: Results per page
        ctx: MCP context
        client: RT client

    Returns:
        Search results
    """
    try:
        await ctx.info(f"Global search: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        if object_type:
            params["type"] = object_type

        # Use generic search endpoint
        results = await client._request("GET", "/search", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} results, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search: {e}")
        raise


@mcp.tool(
    name="bulk_update",
    description="Update multiple objects with progress reporting",
    tags={"search", "write", "power-user"},
    annotations={"title": "Bulk Update RT Objects", "readOnlyHint": False},
)
async def bulk_update(
    object_type: str,
    object_ids: list[int],
    updates: dict,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Bulk update multiple objects with progress reporting.

    Args:
        object_type: Type of object (ticket, asset, etc.)
        object_ids: List of object IDs to update
        updates: Dictionary of updates to apply
        ctx: MCP context
        client: RT client

    Returns:
        Update results with success/failure counts
    """
    try:
        total = len(object_ids)
        await ctx.info(f"Starting bulk update of {total} {object_type}s")

        results = {"success": [], "failed": []}

        for i, obj_id in enumerate(object_ids):
            await ctx.report_progress(i, total, f"Updating {object_type} {obj_id}")

            try:
                # Route to appropriate update method based on type
                if object_type == "ticket":
                    await client.update_ticket(obj_id, updates)
                elif object_type == "asset":
                    await client.update_asset(obj_id, updates)
                elif object_type == "queue":
                    await client.update_queue(obj_id, updates)
                elif object_type == "user":
                    await client.update_user(obj_id, updates)
                else:
                    raise ValueError(f"Unsupported object type: {object_type}")

                results["success"].append(obj_id)
                await ctx.debug(f"✓ Updated {object_type} {obj_id}")
            except Exception as e:
                results["failed"].append({"id": obj_id, "error": str(e)})
                await ctx.warning(f"✗ Failed {object_type} {obj_id}: {e}")

        await ctx.report_progress(total, total, "Complete")

        success_count = len(results["success"])
        failed_count = len(results["failed"])
        await ctx.info(f"✓ Bulk update complete: {success_count} success, {failed_count} failed")

        return {
            "total": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
        }
    except RTError as e:
        await ctx.error(f"Bulk update failed: {e}")
        raise


@mcp.tool(
    name="advanced_ticket_search",
    description="Advanced ticket search with automatic pagination to retrieve all results",
    tags={"search", "read", "power-user"},
    annotations={"title": "Advanced Ticket Search", "readOnlyHint": True},
)
async def advanced_ticket_search(
    query: str,
    max_results: int = 1000,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Advanced ticket search with automatic pagination.

    Args:
        query: RT query string
        max_results: Maximum total results to retrieve (default 1000)
        ctx: MCP context
        client: RT client

    Returns:
        All matching tickets up to max_results
    """
    try:
        await ctx.info(f"Advanced search: {query} (max {max_results} results)")

        all_items = []
        page = 1
        per_page = 100  # Max allowed by RT

        while len(all_items) < max_results:
            await ctx.report_progress(len(all_items), max_results, f"Page {page}")

            response = await client.search_tickets(query, page, per_page)
            items = response.get("items", [])
            all_items.extend(items)

            total = response.get("total", 0)
            pages = response.get("pages", 1)

            await ctx.debug(f"Retrieved page {page}/{pages} ({len(items)} items)")

            if page >= pages or len(items) == 0:
                break

            page += 1

        # Trim to max_results
        all_items = all_items[:max_results]

        await ctx.report_progress(len(all_items), max_results, "Complete")
        await ctx.info(f"✓ Retrieved {len(all_items)} tickets (total available: {total})")

        return {
            "query": query,
            "total_available": total,
            "retrieved_count": len(all_items),
            "max_results": max_results,
            "items": all_items,
        }
    except RTError as e:
        await ctx.error(f"Advanced search failed: {e}")
        raise
