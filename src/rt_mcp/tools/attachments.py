"""MCP tools for RT attachment operations."""

from fastmcp import Context
from fastmcp.dependencies import Depends
from ..application import mcp
from ..dependencies import get_rt_client
from ..client import RTClient
from ..utils.errors import RTError
import base64


@mcp.tool(
    name="get_attachment",
    description="Get attachment metadata by ID",
    tags={"attachments", "read", "basic"},
    annotations={"title": "Get RT Attachment", "readOnlyHint": True},
)
async def get_attachment(
    attachment_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get attachment metadata."""
    try:
        await ctx.info(f"Fetching attachment {attachment_id}")
        attachment = await client.get_attachment(attachment_id)
        await ctx.info(f"✓ Retrieved attachment {attachment_id}")
        return attachment
    except RTError as e:
        await ctx.error(f"Failed to get attachment {attachment_id}: {e}")
        raise


@mcp.tool(
    name="get_attachment_content",
    description="Get attachment content (binary data as base64)",
    tags={"attachments", "read", "basic"},
    annotations={"title": "Get RT Attachment Content", "readOnlyHint": True},
)
async def get_attachment_content(
    attachment_id: int,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Get attachment content."""
    try:
        await ctx.info(f"Fetching content for attachment {attachment_id}")
        content = await client.get_attachment_content(attachment_id)
        # Encode binary content as base64 for JSON transport
        content_b64 = base64.b64encode(content).decode('utf-8')
        await ctx.info(f"✓ Retrieved {len(content)} bytes")
        return {"attachment_id": attachment_id, "content_base64": content_b64, "size_bytes": len(content)}
    except RTError as e:
        await ctx.error(f"Failed to get attachment content: {e}")
        raise


@mcp.tool(
    name="upload_attachment",
    description="Upload an attachment to a ticket",
    tags={"attachments", "write", "basic"},
    annotations={"title": "Upload RT Attachment", "readOnlyHint": False},
)
async def upload_attachment(
    ticket_id: int,
    filename: str,
    content_base64: str,
    ctx: Context = None,
    client: RTClient = Depends(get_rt_client),
) -> dict:
    """Upload attachment to ticket."""
    try:
        await ctx.info(f"Uploading attachment '{filename}' to ticket {ticket_id}")
        # Decode base64 content
        content = base64.b64decode(content_base64)
        result = await client.upload_attachment(ticket_id, filename, content)
        await ctx.info(f"✓ Uploaded attachment ({len(content)} bytes)")
        return result
    except RTError as e:
        await ctx.error(f"Failed to upload attachment: {e}")
        raise
