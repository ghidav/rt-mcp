"""MCP tools for RT transaction operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="get_transaction",
    description="Get transaction details by ID",
    tags={"transactions", "read", "basic"},
    annotations={"title": "Get RT Transaction", "readOnlyHint": True},
)
async def get_transaction(
    transaction_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get transaction details."""
    try:
        await ctx.info(f"Fetching transaction {transaction_id}")
        transaction = await client.get_transaction(transaction_id)
        await ctx.info(f"✓ Retrieved transaction {transaction_id}")
        return transaction
    except RTError as e:
        await ctx.error(f"Failed to get transaction {transaction_id}: {e}")
        raise


@mcp.tool(
    name="list_transactions",
    description="List all transactions",
    tags={"transactions", "read", "basic"},
    annotations={"title": "List RT Transactions", "readOnlyHint": True},
)
async def list_transactions(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """List transactions."""
    try:
        await ctx.info("Fetching transaction list")
        transactions = await client.list_transactions()
        count = transactions.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} transactions")
        return transactions
    except RTError as e:
        await ctx.error(f"Failed to list transactions: {e}")
        raise


@mcp.tool(
    name="search_transactions",
    description="Search transactions with RT query syntax",
    tags={"transactions", "search", "basic"},
    annotations={"title": "Search RT Transactions", "readOnlyHint": True},
)
async def search_transactions(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Search transactions."""
    try:
        await ctx.info(f"Searching transactions: {query}")
        results = await client.search_transactions(query, page, per_page)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} transactions, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search transactions: {e}")
        raise
