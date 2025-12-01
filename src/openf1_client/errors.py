"""
OpenF1 Client Exception Hierarchy.

This module defines a comprehensive exception hierarchy for handling
errors that may occur when interacting with the OpenF1 API.
"""

from __future__ import annotations

from typing import Any


class OpenF1Error(Exception):
    """
    Base exception for all OpenF1 client errors.

    All exceptions raised by the OpenF1 client inherit from this class,
    allowing consumers to catch all client-related errors with a single
    except clause if desired.
    """

    def __init__(self, message: str, *args: Any) -> None:
        """
        Initialize the base error.

        Args:
            message: Human-readable error description.
            *args: Additional positional arguments passed to Exception.
        """
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.message


class OpenF1ConfigError(OpenF1Error):
    """
    Invalid configuration or missing settings.

    Raised when the client is configured with invalid parameters,
    missing required settings, or incompatible option combinations.
    """

    pass


class OpenF1TransportError(OpenF1Error):
    """
    Network or low-level HTTP error.

    Raised when a request fails due to network issues, DNS resolution
    failures, connection timeouts, or other transport-layer problems.
    """

    def __init__(
        self,
        message: str,
        original_error: Exception | None = None,
    ) -> None:
        """
        Initialize the transport error.

        Args:
            message: Human-readable error description.
            original_error: The underlying exception that caused this error.
        """
        super().__init__(message)
        self.original_error = original_error

    def __str__(self) -> str:
        """Return string representation with original error details."""
        if self.original_error:
            return f"{self.message}: {self.original_error}"
        return self.message


class OpenF1APIError(OpenF1Error):
    """
    Non-2xx response from the API.

    Raised when the API returns an error response. This is the base
    class for all API-specific errors and contains response details.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: str | dict[str, Any] | None = None,
        request_url: str | None = None,
    ) -> None:
        """
        Initialize the API error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code from the response.
            response_body: The response body (parsed JSON or raw text).
            request_url: The URL that was requested.
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_url = request_url

    def __str__(self) -> str:
        """Return detailed string representation."""
        parts = [f"{self.message} (HTTP {self.status_code})"]
        if self.request_url:
            parts.append(f"URL: {self.request_url}")
        if self.response_body:
            parts.append(f"Response: {self.response_body}")
        return " | ".join(parts)


class OpenF1AuthError(OpenF1APIError):
    """
    Authentication or authorization failure (401/403).

    Raised when:
    - Authentication credentials are invalid or expired
    - The token has been revoked
    - The user lacks permission to access a resource
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        response_body: str | dict[str, Any] | None = None,
        request_url: str | None = None,
    ) -> None:
        """
        Initialize the authentication error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code (401 or 403).
            response_body: The response body.
            request_url: The URL that was requested.
        """
        super().__init__(message, status_code, response_body, request_url)


class OpenF1RateLimitError(OpenF1APIError):
    """
    Rate limited by the API (429).

    Raised when too many requests have been made in a given time period.
    Contains information about when the client can retry.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response_body: str | dict[str, Any] | None = None,
        request_url: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code (429).
            response_body: The response body.
            request_url: The URL that was requested.
            retry_after: Seconds to wait before retrying (from Retry-After header).
        """
        super().__init__(message, status_code, response_body, request_url)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Return string representation with retry information."""
        base = super().__str__()
        if self.retry_after:
            return f"{base} | Retry after: {self.retry_after}s"
        return base


class OpenF1NotFoundError(OpenF1APIError):
    """
    Resource not found (404).

    Raised when:
    - The requested endpoint does not exist
    - The requested resource (session, driver, etc.) was not found
    - Query parameters don't match any data
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int = 404,
        response_body: str | dict[str, Any] | None = None,
        request_url: str | None = None,
    ) -> None:
        """
        Initialize the not found error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code (404).
            response_body: The response body.
            request_url: The URL that was requested.
        """
        super().__init__(message, status_code, response_body, request_url)


class OpenF1ServerError(OpenF1APIError):
    """
    Server-side error (5xx).

    Raised when the API encounters an internal error. These are typically
    transient and may succeed if retried after a delay.
    """

    def __init__(
        self,
        message: str = "Server error",
        status_code: int = 500,
        response_body: str | dict[str, Any] | None = None,
        request_url: str | None = None,
    ) -> None:
        """
        Initialize the server error.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code (5xx).
            response_body: The response body.
            request_url: The URL that was requested.
        """
        super().__init__(message, status_code, response_body, request_url)


class OpenF1TimeoutError(OpenF1TransportError):
    """
    Request timed out.

    Raised when a request exceeds the configured timeout duration.
    This can happen for large queries or during API slowdowns.
    """

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: float | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """
        Initialize the timeout error.

        Args:
            message: Human-readable error description.
            timeout: The timeout value that was exceeded.
            original_error: The underlying timeout exception.
        """
        super().__init__(message, original_error)
        self.timeout = timeout

    def __str__(self) -> str:
        """Return string representation with timeout details."""
        if self.timeout:
            return f"{self.message} (timeout: {self.timeout}s)"
        return self.message


class OpenF1ValidationError(OpenF1Error):
    """
    Data validation error.

    Raised when response data fails to validate against expected schemas,
    or when invalid parameters are provided to client methods.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """
        Initialize the validation error.

        Args:
            message: Human-readable error description.
            field: The field that failed validation.
            value: The invalid value.
        """
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        """Return string representation with validation details."""
        parts = [self.message]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.value is not None:
            parts.append(f"Value: {self.value!r}")
        return " | ".join(parts)


def raise_for_status(
    status_code: int,
    response_body: str | dict[str, Any] | None = None,
    request_url: str | None = None,
    retry_after: int | None = None,
) -> None:
    """
    Raise an appropriate exception based on HTTP status code.

    This function maps HTTP status codes to the corresponding exception
    classes and raises the appropriate error.

    Args:
        status_code: HTTP status code from the response.
        response_body: The response body (parsed JSON or raw text).
        request_url: The URL that was requested.
        retry_after: Retry-After header value for 429 responses.

    Raises:
        OpenF1AuthError: For 401 or 403 status codes.
        OpenF1NotFoundError: For 404 status codes.
        OpenF1RateLimitError: For 429 status codes.
        OpenF1ServerError: For 5xx status codes.
        OpenF1APIError: For other non-2xx status codes.
    """
    if 200 <= status_code < 300:
        return

    # Construct a default message based on status code
    status_messages = {
        400: "Bad request",
        401: "Authentication required",
        403: "Access forbidden",
        404: "Resource not found",
        405: "Method not allowed",
        408: "Request timeout",
        422: "Validation error",
        429: "Rate limit exceeded",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }
    message = status_messages.get(status_code, f"HTTP error {status_code}")

    # Map to appropriate exception class
    if status_code in (401, 403):
        raise OpenF1AuthError(message, status_code, response_body, request_url)
    elif status_code == 404:
        raise OpenF1NotFoundError(message, status_code, response_body, request_url)
    elif status_code == 429:
        raise OpenF1RateLimitError(
            message, status_code, response_body, request_url, retry_after
        )
    elif 500 <= status_code < 600:
        raise OpenF1ServerError(message, status_code, response_body, request_url)
    else:
        raise OpenF1APIError(message, status_code, response_body, request_url)
