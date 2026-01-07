"""RT MCP Server - Entry point."""

import sys
import inspect
from typing import Any, Dict
from fastmcp.tools.tool import FunctionTool

# --- START MONKEY PATCH FOR N8N COMPATIBILITY ---
# This fixes the issue where n8n sends extra metadata (sessionId, etc.)
# that causes FastMCP strict validation to crash.

_original_run = FunctionTool.run

async def _run_with_arg_sanitizer(self: FunctionTool, arguments: Dict[str, Any]) -> Any: # type: ignore[override]
    """
    Sanitize tool arguments before FastMCP does its strict parameter validation.
    Drops keys that are not in the underlying function's signature.
    """
    # If arguments is not a dict, just pass it through
    if not isinstance(arguments, dict):
        return await _original_run(self, arguments)

    # Cache allowed parameter names for this specific tool to improve performance
    if not hasattr(self, "_allowed_parameter_names"):
        signature = inspect.signature(self.fn)
        self._allowed_parameter_names = tuple(signature.parameters.keys())

    allowed = getattr(self, "_allowed_parameter_names")

    # Create a new dict with ONLY the allowed keys
    sanitized = {k: v for k, v in arguments.items() if k in allowed}

    # Call the original method with clean arguments
    return await _original_run(self, sanitized)

# Apply the patch to the class
FunctionTool.run = _run_with_arg_sanitizer
# --- END MONKEY PATCH ---

from .application import mcp

def main():
    """Entry point for RT MCP server."""
    try:
        # Import all tool modules to register them
        from .tools import tickets  # noqa: F401
        from .tools import queues  # noqa: F401
        from .tools import users  # noqa: F401
        from .tools import groups  # noqa: F401
        from .tools import assets  # noqa: F401
        from .tools import transactions  # noqa: F401
        from .tools import attachments  # noqa: F401
        from .tools import catalogs  # noqa: F401
        from .tools import custom_fields  # noqa: F401
        from .tools import custom_roles  # noqa: F401
        from .tools import search  # noqa: F401

        # Import resources to register them
        from .resources import rt_resources  # noqa: F401

        # Run server with streamable-http transport
        import os
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        
        # Print confirmation so you know the patch is active
        print("Starting RT MCP Server with n8n argument sanitizer active...", file=sys.stderr)
        
        mcp.run(transport="streamable-http", host=host, port=port)
    except Exception as e:
        print(f"Failed to start RT MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()