"""MCP tools for RT user operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="list_users",
    description="List all users in RT",
    tags={"users", "read", "basic"},
    annotations={
        "title": "List RT Users",
        "readOnlyHint": True,
    },
)
async def list_users(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    List all users.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        List of users
    """
    try:
        await ctx.info("Fetching user list")
        users = await client.list_users()
        count = users.get("count", 0)
        await ctx.info(f"✓ Retrieved {count} users")
        return users
    except RTError as e:
        await ctx.error(f"Failed to list users: {e}")
        raise


@mcp.tool(
    name="get_user",
    description="Get user details by ID or username",
    tags={"users", "read", "basic"},
    annotations={
        "title": "Get RT User",
        "readOnlyHint": True,
    },
)
async def get_user(
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get user details by ID or username.

    Args:
        user_id: User ID or username
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        User details
    """
    try:
        await ctx.info(f"Fetching user {user_id}")
        user = await client.get_user(user_id)
        await ctx.info(f"✓ Retrieved user {user_id}")
        return user
    except RTError as e:
        await ctx.error(f"Failed to get user {user_id}: {e}")
        raise


@mcp.tool(
    name="get_current_user",
    description="Get current authenticated user details",
    tags={"users", "read", "basic"},
    annotations={
        "title": "Get Current RT User",
        "readOnlyHint": True,
    },
)
async def get_current_user(
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get current authenticated user details.

    Args:
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Current user details
    """
    try:
        await ctx.info("Fetching current user")
        user = await client.get_current_user()
        username = user.get("Name", "unknown")
        await ctx.info(f"✓ Retrieved current user: {username}")
        return user
    except RTError as e:
        await ctx.error(f"Failed to get current user: {e}")
        raise


@mcp.tool(
    name="create_user",
    description="Create a new user",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Create RT User",
        "readOnlyHint": False,
    },
)
async def create_user(
    name: str,
    email_address: str,
    real_name: str | None = None,
    password: str | None = None,
    privileged: bool = False,
    disabled: bool = False,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Create a new user.

    Args:
        name: Username
        email_address: Email address
        real_name: Real name
        password: Password (optional)
        privileged: Whether user is privileged
        disabled: Whether user is disabled
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Created user data
    """
    try:
        await ctx.info(f"Creating user '{name}'")

        user_data = {
            "Name": name,
            "EmailAddress": email_address,
            "Privileged": 1 if privileged else 0,
            "Disabled": 1 if disabled else 0,
        }
        if real_name:
            user_data["RealName"] = real_name
        if password:
            user_data["Password"] = password

        result = await client.create_user(user_data)
        user_id = result.get("id", "unknown")
        await ctx.info(f"✓ Created user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to create user: {e}")
        raise


@mcp.tool(
    name="update_user",
    description="Update an existing user",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Update RT User",
        "readOnlyHint": False,
    },
)
async def update_user(
    user_id: str | int,
    email_address: str | None = None,
    real_name: str | None = None,
    password: str | None = None,
    privileged: bool | None = None,
    disabled: bool | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Update user details.

    Args:
        user_id: User ID or username
        email_address: New email address
        real_name: New real name
        password: New password
        privileged: Whether user is privileged
        disabled: Whether user is disabled
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Updated user data
    """
    try:
        await ctx.info(f"Updating user {user_id}")

        update_data = {}
        if email_address:
            update_data["EmailAddress"] = email_address
        if real_name:
            update_data["RealName"] = real_name
        if password:
            update_data["Password"] = password
        if privileged is not None:
            update_data["Privileged"] = 1 if privileged else 0
        if disabled is not None:
            update_data["Disabled"] = 1 if disabled else 0

        result = await client.update_user(user_id, update_data)
        await ctx.info(f"✓ Updated user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to update user {user_id}: {e}")
        raise


@mcp.tool(
    name="search_users",
    description="Search users with RT query syntax",
    tags={"users", "search", "basic"},
    annotations={
        "title": "Search RT Users",
        "readOnlyHint": True,
    },
)
async def search_users(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Search users using RT query syntax.

    Args:
        query: RT query string (e.g., "Name LIKE 'john%'")
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Paginated search results
    """
    try:
        await ctx.info(f"Searching users: {query}")
        params = {"query": query, "page": page, "per_page": per_page}
        results = await client._request("GET", "/users", params=params)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} users, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search users: {e}")
        raise


@mcp.tool(
    name="disable_user",
    description="Disable a user account",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Disable RT User",
        "readOnlyHint": False,
        "destructiveHint": True,
    },
)
async def disable_user(
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Disable a user account.

    Args:
        user_id: User ID or username
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of disable operation
    """
    try:
        await ctx.warning(f"Disabling user {user_id}")
        result = await client.update_user(user_id, {"Disabled": 1})
        await ctx.info(f"✓ Disabled user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to disable user {user_id}: {e}")
        raise


@mcp.tool(
    name="enable_user",
    description="Enable a disabled user account",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Enable RT User",
        "readOnlyHint": False,
    },
)
async def enable_user(
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Enable a disabled user account.

    Args:
        user_id: User ID or username
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of enable operation
    """
    try:
        await ctx.info(f"Enabling user {user_id}")
        result = await client.update_user(user_id, {"Disabled": 0})
        await ctx.info(f"✓ Enabled user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to enable user {user_id}: {e}")
        raise


@mcp.tool(
    name="grant_privilege",
    description="Grant privileged access to a user",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Grant RT User Privilege",
        "readOnlyHint": False,
    },
)
async def grant_privilege(
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Grant privileged access to a user.

    Args:
        user_id: User ID or username
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of privilege grant
    """
    try:
        await ctx.info(f"Granting privilege to user {user_id}")
        result = await client.update_user(user_id, {"Privileged": 1})
        await ctx.info(f"✓ Granted privilege to user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to grant privilege to user {user_id}: {e}")
        raise


@mcp.tool(
    name="revoke_privilege",
    description="Revoke privileged access from a user",
    tags={"users", "write", "admin"},
    annotations={
        "title": "Revoke RT User Privilege",
        "readOnlyHint": False,
    },
)
async def revoke_privilege(
    user_id: str | int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Revoke privileged access from a user.

    Args:
        user_id: User ID or username
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of privilege revocation
    """
    try:
        await ctx.warning(f"Revoking privilege from user {user_id}")
        result = await client.update_user(user_id, {"Privileged": 0})
        await ctx.info(f"✓ Revoked privilege from user {user_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to revoke privilege from user {user_id}: {e}")
        raise
