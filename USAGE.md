# RT MCP Server - Usage Guide

## Quick Start

### 1. Configure RT Credentials

Edit `.env` file:

```bash
# For production RT server
RT_URL=https://rt.yourcompany.com
RT_TOKEN=your_actual_token_here
RT_VERIFY_SSL=true

# OR use username/password
RT_URL=https://rt.yourcompany.com
RT_USER=your_username
RT_PASSWORD=your_password
RT_VERIFY_SSL=true
```

### 2. Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python -m rt_mcp.server
```

**Expected Output:**
```
🚀 RT MCP Server starting
   RT URL: https://rt.yourcompany.com
   Auth: Token
   SSL Verify: True
✓ RT connection validated
✓ RT MCP Server ready
```

If RT is unreachable, you'll see:
```
⚠ RT connection not available: Network error: ...
  Server will start anyway - tools will fail if RT is unreachable
✓ RT MCP Server ready
```

The server will still start and tools will work once RT becomes available.

## Using with Claude Desktop

### Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "rt": {
      "command": "/Users/YOUR_USERNAME/Desktop/MMN/rt-mcp/venv/bin/python",
      "args": ["-m", "rt_mcp.server"],
      "env": {
        "RT_URL": "https://rt.yourcompany.com",
        "RT_TOKEN": "your_token_here",
        "RT_VERIFY_SSL": "true"
      }
    }
  }
}
```

**Note:** Replace `/Users/YOUR_USERNAME/Desktop/MMN/rt-mcp/venv/bin/python` with your actual path.

### Restart Claude Desktop

After editing the config, restart Claude Desktop completely (Cmd+Q, then relaunch).

### Verify Connection

In Claude Desktop, you should see the RT server connected. You can ask Claude:

> "What RT tools are available?"

Claude will show you all 34 tools + 4 resources.

## Testing with MCP Inspector

The MCP Inspector is a development tool for testing MCP servers:

```bash
npx @modelcontextprotocol/inspector python -m rt_mcp.server
```

This will:
1. Launch a web interface (usually on http://localhost:5173)
2. Show all available tools and resources
3. Let you test tools with custom inputs
4. Display real-time logs

### Testing Tools

In the Inspector:

1. **Go to Tools tab** - See all 34 tools
2. **Click a tool** - e.g., `create_ticket`
3. **Fill in parameters**:
   ```json
   {
     "queue": "General",
     "subject": "Test ticket from MCP Inspector",
     "content": "This is a test"
   }
   ```
4. **Click "Call Tool"** - See the result
5. **Check logs** - View request/response details

### Testing Resources

In the Inspector:

1. **Go to Resources tab** - See all 4 resources
2. **Click a resource** - e.g., `rt://queues/list`
3. **View content** - See the JSON data returned

## Available Tools by Category

### Ticket Operations (15 tools)

**Basic Operations:**
```python
# Create a ticket
create_ticket(queue="General", subject="Server down", content="Details here")

# Get ticket details
get_ticket(ticket_id=123)

# Update ticket
update_ticket(ticket_id=123, status="resolved", priority=50)

# Search tickets
search_tickets(query="Status = 'new' AND Queue = 'Support'")
```

**Communication:**
```python
# Add customer-visible reply
correspond_ticket(ticket_id=123, content="We're working on it")

# Add internal comment
comment_ticket(ticket_id=123, content="Waiting for hardware")
```

**Ownership:**
```python
# Take ownership
take_ticket(ticket_id=123)

# Steal from another user
steal_ticket(ticket_id=123)

# Release ownership
untake_ticket(ticket_id=123)
```

**Advanced:**
```python
# Merge tickets
merge_tickets(ticket_id=456, into_ticket_id=123)

# Link tickets
link_tickets(ticket_id=123, link_type="DependsOn", target_ticket_id=456)

# Get history
get_ticket_history(ticket_id=123)

# Get attachments
get_ticket_attachments(ticket_id=123)
```

### Queue Operations (8 tools)

```python
# List all queues
list_queues()

# Get queue details
get_queue(queue_id="General")

# Create queue (admin)
create_queue(
    name="Support",
    description="Customer support requests",
    correspond_address="support@company.com"
)

# Update queue (admin)
update_queue(queue_id="Support", description="Updated description")

# Search queues
search_queues(query="Name LIKE 'Dev%'")

# Disable/enable queues (admin)
disable_queue(queue_id="OldQueue")
enable_queue(queue_id="Support")
```

### User Operations (11 tools)

```python
# List all users
list_users()

# Get user details
get_user(user_id="john.doe")

# Get current user
get_current_user()

# Create user (admin)
create_user(
    name="john.doe",
    email_address="john@company.com",
    real_name="John Doe",
    privileged=False
)

# Update user (admin)
update_user(user_id="john.doe", email_address="new@company.com")

# Search users
search_users(query="Name LIKE 'john%'")

# Manage users (admin)
disable_user(user_id="old.user")
enable_user(user_id="john.doe")
grant_privilege(user_id="admin.user")
revoke_privilege(user_id="former.admin")
```

## Available Resources

Resources provide quick access to reference data:

```python
# List all queues (for reference)
rt://queues/list

# List all custom fields
rt://custom-fields/list

# Get current user info
rt://user/current

# Get RT server info
rt://server/info
```

## Tag-Based Filtering

Tools are tagged for easy discovery:

### By Resource Type
- `tickets` - Ticket operations
- `queues` - Queue management
- `users` - User operations

### By Operation Type
- `read` - Safe, read-only operations
- `write` - State-changing operations
- `delete` - Destructive operations
- `search` - Search/query operations

### By Permission Level
- `basic` - Common user operations
- `power-user` - Advanced operations
- `admin` - Administrative functions

**Example in Claude Desktop:**
> "Show me all read-only ticket tools"
>
> Claude will filter for tools with tags: `tickets` + `read`

## Troubleshooting

### Server won't start

**Check Python version:**
```bash
python --version  # Must be 3.10+
```

**Check virtual environment:**
```bash
which python  # Should show venv/bin/python
```

**Check dependencies:**
```bash
pip list | grep fastmcp  # Should show fastmcp 2.14.2+
```

### Connection errors

**Verify RT URL:**
```bash
curl https://your-rt-server.com/REST/2.0/
```

**Check credentials:**
- Token authentication: Ensure `RT_TOKEN` is valid
- Basic auth: Ensure `RT_USER` and `RT_PASSWORD` are correct

**SSL issues:**
```bash
# For self-signed certificates
RT_VERIFY_SSL=false
```

### Tools fail when called

**Check logs:**
The server outputs to stderr, so you'll see errors like:
```
✗ Failed to get ticket 999: Resource not found
```

**Common issues:**
- Invalid ticket ID (404 error)
- Permission denied (403 error)
- Authentication failed (401 error)
- Network timeout (check RT server availability)

### Claude Desktop integration issues

**Server not showing in Claude:**
1. Check config file path is correct
2. Verify JSON syntax is valid
3. Restart Claude Desktop completely
4. Check Claude Desktop logs

**Tools not working:**
1. Verify environment variables in config
2. Check RT credentials are valid
3. Test with MCP Inspector first
4. Look for error messages in server logs

## Advanced Usage

### Custom Configuration

You can override settings per-invocation:

```bash
RT_URL=https://dev-rt.company.com \
RT_TOKEN=dev_token \
python -m rt_mcp.server
```

### Development Mode

For development with auto-reload:

```bash
# Watch for changes and restart
pip install watchdog
watchmedo auto-restart -d src/rt_mcp -p '*.py' -- python -m rt_mcp.server
```

### Production Deployment

For production, consider:

1. **Process manager** (systemd, supervisord)
2. **Logging** to files for debugging
3. **Monitoring** for uptime
4. **Alerts** for connection failures

Example systemd service:

```ini
[Unit]
Description=RT MCP Server
After=network.target

[Service]
Type=simple
User=rt-user
WorkingDirectory=/opt/rt-mcp
Environment="RT_URL=https://rt.company.com"
Environment="RT_TOKEN=production_token"
ExecStart=/opt/rt-mcp/venv/bin/python -m rt_mcp.server
Restart=always

[Install]
WantedBy=multi-user.target
```

## Getting Help

- Check the [RT REST2 API docs](https://docs.bestpractical.com/rt/5.0.0/RT/REST2.html)
- Review the [fastmcp documentation](https://gofastmcp.com/)
- File issues on the project repository
- Check server logs for error messages

## Next Steps

The server currently has 34 tools covering tickets, queues, and users. Future additions:

- **Groups** (8 tools) - Group management
- **Assets** (10 tools) - Asset tracking
- **Transactions** (5 tools) - Transaction details
- **Attachments** (5 tools) - File operations
- **Catalogs** (6 tools) - Catalog management
- **Custom Fields** (8 tools) - Custom field management

Contributions welcome!
