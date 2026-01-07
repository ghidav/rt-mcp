# RT MCP Server

Model Context Protocol (MCP) server for Request Tracker REST2 API built with fastmcp.

## Features

- ✅ Comprehensive RT REST2 API coverage (85+ tools planned)
- ✅ Tag-based tool filtering (resource type, operation, permission level)
- ✅ Advanced fastmcp features (dependency injection, lifespan, Context)
- ✅ Environment variable configuration
- ✅ Type-safe with Pydantic models
- ✅ Async/await throughout
- ✅ Production-ready error handling

## Quick Start

### Installation

```bash
# Clone or navigate to the repository
cd rt-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your RT credentials:

```env
RT_URL=https://your-rt-server.com
RT_TOKEN=your_token_here
# OR
# RT_USER=username
# RT_PASSWORD=password
```

### Running the Server

The server uses **Streamable HTTP** transport (listening on port 8000 by default).

```bash
# Optional: Configure host/port
export HOST=0.0.0.0
export PORT=8000

# Run directly
python -m rt_mcp.server

# Or use the installed command
rt-mcp
```

### Docker 🐳

```bash
# Build and start
docker compose up -d --build
```

The server will be available at `http://localhost:8000/mcp`.

## Available Tools

**Total: 75 tools + 4 resources** - Complete RT REST2 API coverage!

### Ticket Operations (15 tools, tags: `tickets`)
- `create_ticket`, `get_ticket`, `update_ticket`, `delete_ticket`
- `search_tickets`, `correspond_ticket`, `comment_ticket`
- `take_ticket`, `steal_ticket`, `untake_ticket`
- `merge_tickets`, `link_tickets`
- `get_ticket_history`, `get_ticket_attachments`

### Queue Operations (8 tools, tags: `queues`)
- `list_queues`, `get_queue`, `create_queue`, `update_queue`
- `search_queues`, `disable_queue`, `enable_queue`

### User Operations (11 tools, tags: `users`)
- `list_users`, `get_user`, `get_current_user`
- `create_user`, `update_user`, `search_users`
- `disable_user`, `enable_user`
- `grant_privilege`, `revoke_privilege`

### Group Operations (8 tools, tags: `groups`)
- `list_groups`, `get_group`, `create_group`, `update_group`
- `delete_group`, `search_groups`
- `add_group_member`, `remove_group_member`

### Asset Operations (6 tools, tags: `assets`)
- `list_assets`, `get_asset`, `create_asset`
- `update_asset`, `delete_asset`, `search_assets`

### Transaction Operations (3 tools, tags: `transactions`)
- `get_transaction`, `list_transactions`, `search_transactions`

### Attachment Operations (3 tools, tags: `attachments`)
- `get_attachment`, `get_attachment_content`, `upload_attachment`

### Catalog Operations (6 tools, tags: `catalogs`)
- `list_catalogs`, `get_catalog`, `create_catalog`
- `update_catalog`, `delete_catalog`, `search_catalogs`

### Custom Field Operations (6 tools, tags: `custom-fields`)
- `list_custom_fields`, `get_custom_field`, `create_custom_field`
- `update_custom_field`, `delete_custom_field`, `search_custom_fields`

### Custom Role Operations (6 tools, tags: `custom-roles`)
- `list_custom_roles`, `get_custom_role`, `create_custom_role`
- `update_custom_role`, `delete_custom_role`, `search_custom_roles`

### Advanced Search (3 tools, tags: `search`)
- `search_all` - Search across all RT objects
- `bulk_update` - Update multiple objects with progress reporting
- `advanced_ticket_search` - Auto-paginated ticket search

### Resources (4 resources)
- `rt://queues/list` - List all queues
- `rt://custom-fields/list` - List all custom fields
- `rt://user/current` - Current authenticated user
- `rt://server/info` - RT server information

## Tag Taxonomy

Tools are organized with multi-dimensional tags:

### Resource Type
- `tickets` - Ticket operations
- `queues` - Queue management
- `users` - User operations
- `groups` - Group management
- `assets` - Asset tracking
- `catalogs` - Catalog management
- `transactions` - Transaction history
- `attachments` - File operations
- `custom-fields` - Custom field management
- `custom-roles` - Custom role operations

### Operation Type
- `read` - Safe GET operations
- `write` - State-changing operations
- `delete` - Destructive operations
- `search` - Search/query operations

### Permission Level
- `basic` - Common user operations
- `power-user` - Advanced operations
- `admin` - Administrative functions

## Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS).

Since the server runs via **Streamable HTTP / SSE**, configuring it is simple:

```json
{
  "mcpServers": {
    "rt": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

> **Note**: Ensure the server is running (locally or via Docker) before connecting Claude Desktop.

If you prefer to have Claude Desktop manage the process (local only):

```json
{
  "mcpServers": {
    "rt": {
      "command": "/path/to/rt-mcp/venv/bin/python",
      "args": ["-m", "rt_mcp.server"],
      "env": {
        "RT_URL": "https://your-rt-server.com",
        "RT_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Development

### Project Structure

```
src/rt_mcp/
├── __init__.py
├── server.py              # FastMCP server with lifespan
├── config.py              # Pydantic settings (env vars)
├── client.py              # RT REST2 API client (httpx)
├── dependencies.py        # Dependency injection providers
├── models/
│   ├── common.py          # Base Pydantic models
│   └── ...
├── tools/
│   ├── tickets.py         # Ticket tools
│   └── ...                # More tool modules coming
├── resources/
│   └── ...                # MCP resources
└── utils/
    ├── errors.py          # Exception hierarchy
    └── helpers.py
```

### Running Tests

```bash
pytest
pytest --cov=rt_mcp
```

### Code Quality

```bash
# Format
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## Architecture

### Dependency Injection

The server uses fastmcp's dependency injection system:

```python
from fastmcp import Context
from fastmcp.dependencies import Depends
from rt_mcp.dependencies import get_rt_client

@mcp.tool()
async def my_tool(
    ticket_id: int,
    ctx: Context,  # Injected MCP context
    client = Depends(get_rt_client)  # Injected RT client
) -> dict:
    await ctx.info("Processing...")
    return await client.get_ticket(ticket_id)
```

### Lifespan Management

Server validates RT connection on startup:

```python
@asynccontextmanager
async def lifespan(mcp):
    # Startup: validate connection
    config = RTConfig()
    async with RTClient(config) as client:
        await client.validate_connection()

    yield

    # Shutdown: cleanup
```

### Error Handling

Custom exception hierarchy for RT errors:

- `RTAuthenticationError` (401)
- `RTAuthorizationError` (403)
- `RTNotFoundError` (404)
- `RTValidationError` (422)
- `RTConflictError` (409/412)
- `RTNetworkError` (network/timeout)
- `RTAPIError` (generic)

## Roadmap

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Configuration with pydantic-settings
- [x] RT client with httpx
- [x] Error handling
- [x] Dependency injection
- [x] Server initialization

### Phase 2: Core Tools ✅
- [x] Complete ticket tools (15 total)
- [x] Queue tools (8)
- [x] User tools (11)
- [x] MCP resources (4 resources)

### Phase 3: Extended Tools
- [ ] Group tools (8)
- [ ] Asset tools (10)
- [ ] Transaction tools (5)
- [ ] Attachment tools (5)

### Phase 4: Advanced Tools
- [ ] Catalog tools (6)
- [ ] Custom field tools (8)
- [ ] Custom role tools (6)
- [ ] Search tools (3)
- [ ] Resources for reference data

### Phase 5: Polish
- [ ] Comprehensive tests (>80% coverage)
- [ ] Complete documentation
- [ ] Performance optimization
- [ ] CI/CD pipeline

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code quality checks pass
5. Submit a pull request

## License

MIT License

## Links

- [Request Tracker Documentation](https://docs.bestpractical.com/rt/)
- [RT REST2 API Reference](https://docs.bestpractical.com/rt/5.0.0/RT/REST2.html)
- [fastmcp Documentation](https://gofastmcp.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
