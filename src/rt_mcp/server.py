"""RT MCP Server - Entry point."""

import sys
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
        mcp.run(transport="streamable-http", host=host, port=port)
    except Exception as e:
        print(f"Failed to start RT MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
