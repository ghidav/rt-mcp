"""Custom exception hierarchy for RT MCP server."""


class RTError(Exception):
    """Base exception for RT MCP server errors."""

    pass


class RTAuthenticationError(RTError):
    """Authentication failed (401)."""

    pass


class RTAuthorizationError(RTError):
    """User lacks permissions for operation (403)."""

    pass


class RTNotFoundError(RTError):
    """Resource not found (404)."""

    pass


class RTValidationError(RTError):
    """Request validation failed (422)."""

    pass


class RTConflictError(RTError):
    """Conflict detected, e.g., ETag mismatch (409/412)."""

    pass


class RTNetworkError(RTError):
    """Network or connection error."""

    pass


class RTAPIError(RTError):
    """Generic API error with status code and details."""

    def __init__(self, status_code: int, message: str, response_body: dict | None = None):
        """
        Initialize RT API error.

        Args:
            status_code: HTTP status code
            message: Error message
            response_body: Optional response body with additional details
        """
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(f"RT API Error {status_code}: {message}")
