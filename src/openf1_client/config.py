"""
OpenF1 Client Configuration.

This module provides configuration management for the OpenF1 client,
including settings for authentication, timeouts, retries, and output formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from openf1_client.errors import OpenF1ConfigError


# Default configuration values
DEFAULT_BASE_URL = "https://api.openf1.org/v1"
DEFAULT_TOKEN_URL = "https://api.openf1.org/token"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_USER_AGENT = "openf1-python-client/1.0.0"


@dataclass
class ClientConfig:
    """
    Configuration for the OpenF1 client.

    This class holds all configuration options for the client, including
    connection settings, authentication credentials, and behavior preferences.

    Attributes:
        base_url: The base URL for the OpenF1 API.
        token_url: The URL for obtaining OAuth2 tokens.
        timeout: Request timeout in seconds. Can be a single float for both
            connect and read timeouts, or a tuple of (connect, read) timeouts.
        max_retries: Maximum number of retry attempts for failed requests.
        username: Username for OAuth2 authentication (optional).
        password: Password for OAuth2 authentication (optional).
        access_token: Pre-existing access token (optional).
        default_format: Default response format ("json" or "csv").
        user_agent: User-Agent header value for requests.
        extra_headers: Additional headers to include in all requests.
        verify_ssl: Whether to verify SSL certificates.
        retry_on_status: HTTP status codes that should trigger a retry.

    Example:
        >>> config = ClientConfig(
        ...     timeout=60.0,
        ...     max_retries=5,
        ...     username="user@example.com",
        ...     password="secret",
        ... )
    """

    base_url: str = DEFAULT_BASE_URL
    token_url: str = DEFAULT_TOKEN_URL
    timeout: float | tuple[float, float] = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    username: str | None = None
    password: str | None = None
    access_token: str | None = None
    default_format: Literal["json", "csv"] = "json"
    user_agent: str = DEFAULT_USER_AGENT
    extra_headers: dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    retry_on_status: tuple[int, ...] = (500, 502, 503, 504)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            OpenF1ConfigError: If any configuration value is invalid.
        """
        # Validate base URL
        if not self.base_url:
            raise OpenF1ConfigError("base_url cannot be empty")
        if not self.base_url.startswith(("http://", "https://")):
            raise OpenF1ConfigError(
                f"base_url must start with http:// or https://: {self.base_url}"
            )

        # Validate timeout
        if isinstance(self.timeout, (int, float)):
            if self.timeout <= 0:
                raise OpenF1ConfigError(f"timeout must be positive: {self.timeout}")
        elif isinstance(self.timeout, tuple):
            if len(self.timeout) != 2:
                raise OpenF1ConfigError(
                    f"timeout tuple must have exactly 2 values: {self.timeout}"
                )
            if any(t <= 0 for t in self.timeout):
                raise OpenF1ConfigError(
                    f"timeout values must be positive: {self.timeout}"
                )

        # Validate max_retries
        if self.max_retries < 0:
            raise OpenF1ConfigError(
                f"max_retries cannot be negative: {self.max_retries}"
            )

        # Validate auth configuration
        if (self.username is None) != (self.password is None):
            raise OpenF1ConfigError(
                "Both username and password must be provided together, or neither"
            )

        # Validate default_format
        if self.default_format not in ("json", "csv"):
            raise OpenF1ConfigError(
                f"default_format must be 'json' or 'csv': {self.default_format}"
            )

    @property
    def has_credentials(self) -> bool:
        """Check if authentication credentials are configured."""
        return self.username is not None and self.password is not None

    @property
    def has_token(self) -> bool:
        """Check if an access token is available."""
        return self.access_token is not None

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is configured for authenticated requests."""
        return self.has_token or self.has_credentials

    def get_timeout(self) -> float | tuple[float, float]:
        """
        Get the timeout configuration.

        Returns:
            The timeout value(s) for requests.
        """
        return self.timeout

    def get_connect_timeout(self) -> float:
        """
        Get the connection timeout.

        Returns:
            The connection timeout in seconds.
        """
        if isinstance(self.timeout, tuple):
            return self.timeout[0]
        return self.timeout

    def get_read_timeout(self) -> float:
        """
        Get the read timeout.

        Returns:
            The read timeout in seconds.
        """
        if isinstance(self.timeout, tuple):
            return self.timeout[1]
        return self.timeout

    def get_headers(self) -> dict[str, str]:
        """
        Get all headers to include in requests.

        Returns:
            A dictionary of headers including User-Agent and any extra headers.
        """
        headers = {"User-Agent": self.user_agent}
        headers.update(self.extra_headers)
        return headers

    def with_token(self, access_token: str) -> "ClientConfig":
        """
        Create a new config with the specified access token.

        This method returns a new ClientConfig instance with the token set,
        leaving the original config unchanged.

        Args:
            access_token: The OAuth2 access token.

        Returns:
            A new ClientConfig with the access token set.
        """
        return ClientConfig(
            base_url=self.base_url,
            token_url=self.token_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            username=self.username,
            password=self.password,
            access_token=access_token,
            default_format=self.default_format,
            user_agent=self.user_agent,
            extra_headers=self.extra_headers.copy(),
            verify_ssl=self.verify_ssl,
            retry_on_status=self.retry_on_status,
        )

    def copy(self, **updates: object) -> "ClientConfig":
        """
        Create a copy of this config with optional updates.

        Args:
            **updates: Fields to update in the new config.

        Returns:
            A new ClientConfig with the specified updates.
        """
        return ClientConfig(
            base_url=updates.get("base_url", self.base_url),  # type: ignore
            token_url=updates.get("token_url", self.token_url),  # type: ignore
            timeout=updates.get("timeout", self.timeout),  # type: ignore
            max_retries=updates.get("max_retries", self.max_retries),  # type: ignore
            username=updates.get("username", self.username),  # type: ignore
            password=updates.get("password", self.password),  # type: ignore
            access_token=updates.get("access_token", self.access_token),  # type: ignore
            default_format=updates.get(
                "default_format", self.default_format
            ),  # type: ignore
            user_agent=updates.get("user_agent", self.user_agent),  # type: ignore
            extra_headers=updates.get(
                "extra_headers", self.extra_headers.copy()
            ),  # type: ignore
            verify_ssl=updates.get("verify_ssl", self.verify_ssl),  # type: ignore
            retry_on_status=updates.get(
                "retry_on_status", self.retry_on_status
            ),  # type: ignore
        )
