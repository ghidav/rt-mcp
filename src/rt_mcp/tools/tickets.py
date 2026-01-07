"""MCP tools for RT ticket operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError


@mcp.tool(
    name="create_ticket",
    description="Create a new ticket in Request Tracker",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Create RT Ticket",
        "readOnlyHint": False,
    },
)
async def create_ticket(
    queue: str,
    subject: str,
    requestor: str | None = None,
    content: str | None = None,
    priority: int = 0,
    status: str = "new",
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Create a new ticket.

    Args:
        queue: Queue name or ID
        subject: Ticket subject
        requestor: Requestor email
        content: Ticket content
        priority: Priority 0-99
        status: Initial status (default: new)
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Created ticket data
    """
    try:
        await ctx.info(f"Creating ticket in '{queue}': {subject}")

        ticket_data = {
            "Queue": queue,
            "Subject": subject,
            "Priority": priority,
            "Status": status,
        }
        if requestor:
            ticket_data["Requestor"] = requestor
        if content:
            ticket_data["Content"] = content

        result = await client.create_ticket(ticket_data)
        ticket_id = result.get("id", "unknown")

        await ctx.info(f"✓ Created ticket {ticket_id}")
        return result

    except RTError as e:
        await ctx.error(f"Failed to create ticket: {e}")
        raise


@mcp.tool(
    name="get_ticket",
    description="Get ticket details by ID",
    tags={"tickets", "read", "basic"},
    annotations={
        "title": "Get RT Ticket",
        "readOnlyHint": True,
    },
)
async def get_ticket(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get ticket by ID.

    Args:
        ticket_id: Numeric ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Complete ticket data
    """
    try:
        await ctx.info(f"Fetching ticket {ticket_id}")
        ticket = await client.get_ticket(ticket_id)
        await ctx.info(f"✓ Retrieved ticket {ticket_id}")
        return ticket
    except RTError as e:
        await ctx.error(f"Failed to get ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="update_ticket",
    description="Update an existing ticket",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Update RT Ticket",
        "readOnlyHint": False,
    },
)
async def update_ticket(
    ticket_id: int,
    subject: str | None = None,
    status: str | None = None,
    priority: int | None = None,
    owner: str | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Update ticket fields.

    Args:
        ticket_id: Ticket ID
        subject: New subject
        status: New status
        priority: New priority
        owner: New owner
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Updated ticket data
    """
    try:
        await ctx.info(f"Updating ticket {ticket_id}")

        update_data = {}
        if subject is not None:
            update_data["Subject"] = subject
        if status is not None:
            update_data["Status"] = status
        if priority is not None:
            update_data["Priority"] = priority
        if owner is not None:
            update_data["Owner"] = owner

        result = await client.update_ticket(ticket_id, update_data)
        await ctx.info(f"✓ Updated ticket {ticket_id}")
        return result

    except RTError as e:
        await ctx.error(f"Failed to update ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="delete_ticket",
    description="Delete (disable) a ticket",
    tags={"tickets", "delete", "admin"},
    annotations={
        "title": "Delete RT Ticket",
        "readOnlyHint": False,
        "destructiveHint": True,
    },
)
async def delete_ticket(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Delete (disable) a ticket.

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of deletion
    """
    try:
        await ctx.warning(f"Deleting ticket {ticket_id}")
        result = await client.delete_ticket(ticket_id)
        await ctx.info(f"✓ Deleted ticket {ticket_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to delete ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="search_tickets",
    description="Search tickets with RT query syntax",
    tags={"tickets", "search", "basic"},
    annotations={
        "title": "Search RT Tickets",
        "readOnlyHint": True,
    },
)
async def search_tickets(
    query: str,
    page: int = 1,
    per_page: int = 20,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Search tickets using RT query syntax.

    Args:
        query: RT query string (e.g., "Status = 'new' AND Queue = 'General'")
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Paginated search results
    """
    try:
        await ctx.info(f"Searching tickets: {query}")
        results = await client.search_tickets(query, page, per_page)
        count = results.get("count", 0)
        total = results.get("total", 0)
        await ctx.info(f"✓ Found {total} tickets, showing {count} on page {page}")
        return results
    except RTError as e:
        await ctx.error(f"Failed to search tickets: {e}")
        raise


@mcp.tool(
    name="correspond_ticket",
    description="Add correspondence (customer-visible reply) to a ticket",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Correspond on RT Ticket",
        "readOnlyHint": False,
    },
)
async def correspond_ticket(
    ticket_id: int,
    content: str,
    cc: str | list[str] | None = None,
    bcc: str | list[str] | None = None,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Add correspondence to a ticket (customer-visible).

    Args:
        ticket_id: Ticket ID
        content: Reply content
        cc: Additional CC recipients
        bcc: Additional BCC recipients
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of correspondence operation
    """
    try:
        await ctx.info(f"Adding correspondence to ticket {ticket_id}")

        correspond_data = {"Content": content}
        if cc:
            correspond_data["Cc"] = cc
        if bcc:
            correspond_data["Bcc"] = bcc

        result = await client.correspond_ticket(ticket_id, correspond_data)
        await ctx.info(f"✓ Added correspondence to ticket {ticket_id}")
        return result

    except RTError as e:
        await ctx.error(f"Failed to correspond on ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="comment_ticket",
    description="Add internal comment (not visible to customer) to a ticket",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Comment on RT Ticket",
        "readOnlyHint": False,
    },
)
async def comment_ticket(
    ticket_id: int,
    content: str,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Add internal comment to a ticket (not customer-visible).

    Args:
        ticket_id: Ticket ID
        content: Comment content
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of comment operation
    """
    try:
        await ctx.info(f"Adding comment to ticket {ticket_id}")

        comment_data = {"Content": content}
        result = await client.comment_ticket(ticket_id, comment_data)
        await ctx.info(f"✓ Added comment to ticket {ticket_id}")
        return result

    except RTError as e:
        await ctx.error(f"Failed to comment on ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="take_ticket",
    description="Take ownership of a ticket",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Take Ownership of RT Ticket",
        "readOnlyHint": False,
    },
)
async def take_ticket(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Take ownership of a ticket (assign to current user).

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of take operation
    """
    try:
        await ctx.info(f"Taking ownership of ticket {ticket_id}")
        result = await client.take_ticket(ticket_id)
        await ctx.info(f"✓ Took ownership of ticket {ticket_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to take ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="steal_ticket",
    description="Steal ownership of a ticket from another user",
    tags={"tickets", "write", "power-user"},
    annotations={
        "title": "Steal RT Ticket Ownership",
        "readOnlyHint": False,
    },
)
async def steal_ticket(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Steal ownership of a ticket from another user.

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of steal operation
    """
    try:
        await ctx.warning(f"Stealing ownership of ticket {ticket_id}")
        result = await client.steal_ticket(ticket_id)
        await ctx.info(f"✓ Stole ownership of ticket {ticket_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to steal ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="untake_ticket",
    description="Release ownership of a ticket (set owner to Nobody)",
    tags={"tickets", "write", "basic"},
    annotations={
        "title": "Release RT Ticket Ownership",
        "readOnlyHint": False,
    },
)
async def untake_ticket(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Release ownership of a ticket (set owner to Nobody).

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of untake operation
    """
    try:
        await ctx.info(f"Releasing ownership of ticket {ticket_id}")
        result = await client.untake_ticket(ticket_id)
        await ctx.info(f"✓ Released ownership of ticket {ticket_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to untake ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="merge_tickets",
    description="Merge one ticket into another",
    tags={"tickets", "write", "power-user"},
    annotations={
        "title": "Merge RT Tickets",
        "readOnlyHint": False,
        "destructiveHint": True,
    },
)
async def merge_tickets(
    ticket_id: int,
    into_ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Merge one ticket into another.

    Args:
        ticket_id: Ticket ID to merge from
        into_ticket_id: Ticket ID to merge into
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of merge operation
    """
    try:
        await ctx.warning(f"Merging ticket {ticket_id} into {into_ticket_id}")
        result = await client.merge_tickets(ticket_id, into_ticket_id)
        await ctx.info(f"✓ Merged ticket {ticket_id} into {into_ticket_id}")
        return result
    except RTError as e:
        await ctx.error(f"Failed to merge tickets: {e}")
        raise


@mcp.tool(
    name="get_ticket_history",
    description="Get transaction history for a ticket",
    tags={"tickets", "read", "basic"},
    annotations={
        "title": "Get RT Ticket History",
        "readOnlyHint": True,
    },
)
async def get_ticket_history(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get transaction history for a ticket.

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Ticket transaction history
    """
    try:
        await ctx.info(f"Fetching history for ticket {ticket_id}")
        history = await client.get_ticket_history(ticket_id)
        await ctx.info(f"✓ Retrieved history for ticket {ticket_id}")
        return history
    except RTError as e:
        await ctx.error(f"Failed to get history for ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="get_ticket_attachments",
    description="Get attachments for a ticket",
    tags={"tickets", "read", "basic"},
    annotations={
        "title": "Get RT Ticket Attachments",
        "readOnlyHint": True,
    },
)
async def get_ticket_attachments(
    ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Get attachments for a ticket.

    Args:
        ticket_id: Ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Ticket attachments list
    """
    try:
        await ctx.info(f"Fetching attachments for ticket {ticket_id}")
        attachments = await client.get_ticket_attachments(ticket_id)
        await ctx.info(f"✓ Retrieved attachments for ticket {ticket_id}")
        return attachments
    except RTError as e:
        await ctx.error(f"Failed to get attachments for ticket {ticket_id}: {e}")
        raise


@mcp.tool(
    name="link_tickets",
    description="Create links between tickets",
    tags={"tickets", "write", "power-user"},
    annotations={
        "title": "Link RT Tickets",
        "readOnlyHint": False,
    },
)
async def link_tickets(
    ticket_id: int,
    link_type: str,
    target_ticket_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """
    Create links between tickets.

    Args:
        ticket_id: Source ticket ID
        link_type: Link type (DependsOn, DependedOnBy, RefersTo, ReferredToBy, etc.)
        target_ticket_id: Target ticket ID
        ctx: MCP context (injected)
        client: RT client (injected)

    Returns:
        Result of link operation
    """
    try:
        await ctx.info(f"Creating {link_type} link from ticket {ticket_id} to {target_ticket_id}")
        link_data = {link_type: target_ticket_id}
        result = await client.link_tickets(ticket_id, link_data)
        await ctx.info(f"✓ Created link between tickets")
        return result
    except RTError as e:
        await ctx.error(f"Failed to link tickets: {e}")
        raise
