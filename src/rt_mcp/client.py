"""RT REST2 API client using httpx."""

import httpx
from .config import RTConfig
from .utils.errors import (
    RTAPIError,
    RTAuthenticationError,
    RTAuthorizationError,
    RTConflictError,
    RTNetworkError,
    RTNotFoundError,
    RTValidationError,
)


class RTClient:
    """Async HTTP client for RT REST2 API."""

    def __init__(self, config: RTConfig):
        """
        Initialize RT client.

        Args:
            config: RT configuration with URL and credentials
        """
        self.config = config
        self.base_url = config.base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Context manager entry - create HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                **self.config.get_auth_header(),
            },
            timeout=self.config.rt_timeout,
            verify=self.config.rt_verify_ssl,
        )
        return self

    async def __aexit__(self, *args):
        """Context manager exit - close HTTP client."""
        if self._client:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            **kwargs: Additional arguments for httpx request

        Returns:
            Response data as dict

        Raises:
            RTNetworkError: On network/timeout errors
            RT*Error: On various API errors
        """
        try:
            response = await self._client.request(method, path, **kwargs)
            return await self._handle_response(response)
        except httpx.NetworkError as e:
            raise RTNetworkError(f"Network error: {e}")
        except httpx.TimeoutException:
            raise RTNetworkError("Request timeout")

    async def _handle_response(self, response: httpx.Response) -> dict:
        """
        Parse response and raise appropriate exceptions.

        Args:
            response: HTTP response

        Returns:
            Response data as dict

        Raises:
            RT*Error: Various error types based on status code
        """
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        if response.status_code in (200, 201):
            return data
        elif response.status_code == 304:
            return {"_status": "not_modified"}
        elif response.status_code == 401:
            raise RTAuthenticationError(
                f"Authentication failed: {data.get('message', '')}"
            )
        elif response.status_code == 403:
            raise RTAuthorizationError(
                f"Permission denied: {data.get('message', '')}"
            )
        elif response.status_code == 404:
            raise RTNotFoundError(f"Resource not found: {data.get('message', '')}")
        elif response.status_code in (409, 412):
            raise RTConflictError(f"Conflict: {data.get('message', '')}")
        elif response.status_code == 422:
            raise RTValidationError(
                f"Validation error: {data.get('message', '')}"
            )
        else:
            raise RTAPIError(
                response.status_code, data.get("message", "Unknown error"), data
            )

    async def validate_connection(self):
        """Test RT connection by making a simple request."""
        await self._request("GET", "/queues")

    # Ticket operations
    async def get_ticket(self, ticket_id: int) -> dict:
        """Get ticket by ID."""
        return await self._request("GET", f"/ticket/{ticket_id}")

    async def create_ticket(self, data: dict) -> dict:
        """Create new ticket."""
        return await self._request("POST", "/ticket", json=data)

    async def update_ticket(
        self, ticket_id: int, data: dict, etag: str | None = None
    ) -> dict:
        """
        Update ticket with optional ETag for conflict detection.

        Args:
            ticket_id: Ticket ID
            data: Update data
            etag: Optional ETag for optimistic locking

        Returns:
            Updated ticket data
        """
        headers = {"If-Match": etag} if etag else {}
        return await self._request(
            "PUT", f"/ticket/{ticket_id}", json=data, headers=headers
        )

    async def delete_ticket(self, ticket_id: int) -> dict:
        """Delete (disable) ticket."""
        return await self._request("DELETE", f"/ticket/{ticket_id}")

    async def search_tickets(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """
        Search tickets with pagination.

        Args:
            query: RT query string
            page: Page number (1-indexed)
            per_page: Items per page (max 100)

        Returns:
            Paginated response with tickets
        """
        params = {"query": query, "page": page, "per_page": per_page}
        return await self._request("GET", "/tickets", params=params)

    async def correspond_ticket(self, ticket_id: int, data: dict) -> dict:
        """Add correspondence (customer-visible) to ticket."""
        return await self._request("POST", f"/ticket/{ticket_id}/correspond", json=data)

    async def comment_ticket(self, ticket_id: int, data: dict) -> dict:
        """Add comment (internal) to ticket."""
        return await self._request("POST", f"/ticket/{ticket_id}/comment", json=data)

    async def take_ticket(self, ticket_id: int) -> dict:
        """Take ownership of a ticket."""
        return await self._request("PUT", f"/ticket/{ticket_id}/take")

    async def steal_ticket(self, ticket_id: int) -> dict:
        """Steal ownership of a ticket from another user."""
        return await self._request("PUT", f"/ticket/{ticket_id}/steal")

    async def untake_ticket(self, ticket_id: int) -> dict:
        """Release ownership of a ticket (set owner to Nobody)."""
        return await self._request("PUT", f"/ticket/{ticket_id}/untake")

    async def get_ticket_history(self, ticket_id: int) -> dict:
        """Get ticket transaction history."""
        return await self._request("GET", f"/ticket/{ticket_id}/history")

    async def get_ticket_attachments(self, ticket_id: int) -> dict:
        """Get ticket attachments."""
        return await self._request("GET", f"/ticket/{ticket_id}/attachments")

    async def link_tickets(self, ticket_id: int, data: dict) -> dict:
        """Create links between tickets."""
        return await self._request("POST", f"/ticket/{ticket_id}/links", json=data)

    async def merge_tickets(self, ticket_id: int, into_ticket_id: int) -> dict:
        """Merge ticket into another ticket."""
        data = {"Into": into_ticket_id}
        return await self._request("POST", f"/ticket/{ticket_id}/merge", json=data)

    # Queue operations
    async def list_queues(self) -> dict:
        """List all queues."""
        return await self._request("GET", "/queues")

    async def get_queue(self, queue_id: int | str) -> dict:
        """Get queue by ID or name."""
        return await self._request("GET", f"/queue/{queue_id}")

    async def create_queue(self, data: dict) -> dict:
        """Create new queue."""
        return await self._request("POST", "/queue", json=data)

    async def update_queue(self, queue_id: int | str, data: dict) -> dict:
        """Update queue."""
        return await self._request("PUT", f"/queue/{queue_id}", json=data)

    # User operations
    async def list_users(self) -> dict:
        """List all users."""
        return await self._request("GET", "/users")

    async def get_user(self, user_id: int | str) -> dict:
        """Get user by ID or name."""
        return await self._request("GET", f"/user/{user_id}")

    async def create_user(self, data: dict) -> dict:
        """Create new user."""
        return await self._request("POST", "/user", json=data)

    async def update_user(self, user_id: int | str, data: dict) -> dict:
        """Update user."""
        return await self._request("PUT", f"/user/{user_id}", json=data)

    async def get_current_user(self) -> dict:
        """Get current authenticated user."""
        return await self._request("GET", "/user/current")

    # Custom field operations
    async def list_custom_fields(self) -> dict:
        """List all custom fields."""
        return await self._request("GET", "/customfields")

    async def get_custom_field(self, field_id: int | str) -> dict:
        """Get custom field by ID."""
        return await self._request("GET", f"/customfield/{field_id}")

    async def create_custom_field(self, data: dict) -> dict:
        """Create new custom field."""
        return await self._request("POST", "/customfield", json=data)

    async def update_custom_field(self, field_id: int | str, data: dict) -> dict:
        """Update custom field."""
        return await self._request("PUT", f"/customfield/{field_id}", json=data)

    async def delete_custom_field(self, field_id: int | str) -> dict:
        """Delete custom field."""
        return await self._request("DELETE", f"/customfield/{field_id}")

    # Group operations
    async def list_groups(self) -> dict:
        """List all groups."""
        return await self._request("GET", "/groups")

    async def get_group(self, group_id: int | str) -> dict:
        """Get group by ID or name."""
        return await self._request("GET", f"/group/{group_id}")

    async def create_group(self, data: dict) -> dict:
        """Create new group."""
        return await self._request("POST", "/group", json=data)

    async def update_group(self, group_id: int | str, data: dict) -> dict:
        """Update group."""
        return await self._request("PUT", f"/group/{group_id}", json=data)

    async def delete_group(self, group_id: int | str) -> dict:
        """Delete group."""
        return await self._request("DELETE", f"/group/{group_id}")

    async def add_group_member(self, group_id: int | str, user_id: int | str) -> dict:
        """Add user to group."""
        return await self._request("POST", f"/group/{group_id}/member", json={"UserId": user_id})

    async def remove_group_member(self, group_id: int | str, user_id: int | str) -> dict:
        """Remove user from group."""
        return await self._request("DELETE", f"/group/{group_id}/member/{user_id}")

    # Asset operations
    async def list_assets(self) -> dict:
        """List all assets."""
        return await self._request("GET", "/assets")

    async def get_asset(self, asset_id: int) -> dict:
        """Get asset by ID."""
        return await self._request("GET", f"/asset/{asset_id}")

    async def create_asset(self, data: dict) -> dict:
        """Create new asset."""
        return await self._request("POST", "/asset", json=data)

    async def update_asset(self, asset_id: int, data: dict) -> dict:
        """Update asset."""
        return await self._request("PUT", f"/asset/{asset_id}", json=data)

    async def delete_asset(self, asset_id: int) -> dict:
        """Delete asset."""
        return await self._request("DELETE", f"/asset/{asset_id}")

    async def search_assets(self, query: str, page: int = 1, per_page: int = 20) -> dict:
        """Search assets."""
        params = {"query": query, "page": page, "per_page": per_page}
        return await self._request("GET", "/assets", params=params)

    # Catalog operations
    async def list_catalogs(self) -> dict:
        """List all catalogs."""
        return await self._request("GET", "/catalogs")

    async def get_catalog(self, catalog_id: int | str) -> dict:
        """Get catalog by ID or name."""
        return await self._request("GET", f"/catalog/{catalog_id}")

    async def create_catalog(self, data: dict) -> dict:
        """Create new catalog."""
        return await self._request("POST", "/catalog", json=data)

    async def update_catalog(self, catalog_id: int | str, data: dict) -> dict:
        """Update catalog."""
        return await self._request("PUT", f"/catalog/{catalog_id}", json=data)

    async def delete_catalog(self, catalog_id: int | str) -> dict:
        """Delete catalog."""
        return await self._request("DELETE", f"/catalog/{catalog_id}")

    # Transaction operations
    async def get_transaction(self, transaction_id: int) -> dict:
        """Get transaction by ID."""
        return await self._request("GET", f"/transaction/{transaction_id}")

    async def list_transactions(self) -> dict:
        """List transactions."""
        return await self._request("GET", "/transactions")

    async def search_transactions(self, query: str, page: int = 1, per_page: int = 20) -> dict:
        """Search transactions."""
        params = {"query": query, "page": page, "per_page": per_page}
        return await self._request("GET", "/transactions", params=params)

    # Attachment operations
    async def get_attachment(self, attachment_id: int) -> dict:
        """Get attachment by ID."""
        return await self._request("GET", f"/attachment/{attachment_id}")

    async def get_attachment_content(self, attachment_id: int) -> bytes:
        """Get attachment content (binary)."""
        response = await self._client.get(f"/attachment/{attachment_id}/content")
        return response.content

    async def upload_attachment(self, ticket_id: int, filename: str, content: bytes) -> dict:
        """Upload attachment to ticket."""
        files = {"attachment": (filename, content)}
        return await self._request("POST", f"/ticket/{ticket_id}/attach", files=files)

    # Custom role operations
    async def list_custom_roles(self) -> dict:
        """List all custom roles."""
        return await self._request("GET", "/customroles")

    async def get_custom_role(self, role_id: int | str) -> dict:
        """Get custom role by ID or name."""
        return await self._request("GET", f"/customrole/{role_id}")

    async def create_custom_role(self, data: dict) -> dict:
        """Create new custom role."""
        return await self._request("POST", "/customrole", json=data)

    async def update_custom_role(self, role_id: int | str, data: dict) -> dict:
        """Update custom role."""
        return await self._request("PUT", f"/customrole/{role_id}", json=data)

    async def delete_custom_role(self, role_id: int | str) -> dict:
        """Delete custom role."""
        return await self._request("DELETE", f"/customrole/{role_id}")
