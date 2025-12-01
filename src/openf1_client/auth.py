"""
OpenF1 Authentication Module.

This module handles OAuth2 authentication for the OpenF1 API,
including token acquisition, storage, and management.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from openf1_client.errors import OpenF1AuthError, OpenF1ConfigError


if TYPE_CHECKING:
    from openf1_client.http_client import OpenF1Transport


logger = logging.getLogger("openf1_client")


@dataclass
class TokenInfo:
    """
    Container for OAuth2 token information.

    Attributes:
        access_token: The access token string.
        token_type: The token type (usually "bearer").
        expires_in: Token lifetime in seconds (if provided).
        expires_at: Unix timestamp when the token expires (if calculable).
        scope: Token scope (if provided).
        refresh_token: Refresh token for obtaining new access tokens (if provided).
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    expires_at: float | None = None
    scope: str | None = None
    refresh_token: str | None = None

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> "TokenInfo":
        """
        Create a TokenInfo from an OAuth2 token response.

        Args:
            data: The token response dictionary.

        Returns:
            A TokenInfo instance.

        Raises:
            OpenF1AuthError: If the response is missing required fields.
        """
        access_token = data.get("access_token")
        if not access_token:
            raise OpenF1AuthError(
                message="Token response missing access_token",
                status_code=0,
                response_body=data,
            )

        expires_in = data.get("expires_in")
        expires_at = None
        if expires_in is not None:
            expires_at = time.time() + expires_in

        return cls(
            access_token=access_token,
            token_type=data.get("token_type", "bearer"),
            expires_in=expires_in,
            expires_at=expires_at,
            scope=data.get("scope"),
            refresh_token=data.get("refresh_token"),
        )

    @property
    def is_expired(self) -> bool:
        """
        Check if the token has expired.

        Returns:
            True if the token has expired, False otherwise.
            Returns False if expiration time is unknown.
        """
        if self.expires_at is None:
            return False
        # Consider expired 60 seconds before actual expiration for safety
        return time.time() >= (self.expires_at - 60)


class AuthProviderProtocol(ABC):
    """
    Abstract base class for authentication providers.

    This protocol defines the interface for authentication mechanisms,
    allowing for different authentication strategies to be implemented.
    """

    @abstractmethod
    def get_token(self) -> str | None:
        """
        Get the current access token.

        Returns:
            The access token string, or None if not authenticated.
        """
        ...

    @abstractmethod
    def authenticate(self) -> TokenInfo:
        """
        Perform authentication and obtain a token.

        Returns:
            The token information.

        Raises:
            OpenF1AuthError: If authentication fails.
        """
        ...

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the client is currently authenticated.

        Returns:
            True if authenticated with a valid token.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear any stored authentication state."""
        ...


class PasswordAuthProvider(AuthProviderProtocol):
    """
    OAuth2 password grant authentication provider.

    This provider implements the OAuth2 password grant flow,
    where the client exchanges a username and password for an access token.

    Attributes:
        username: The username for authentication.
        password: The password for authentication.
        token_url: The URL for the token endpoint.
    """

    def __init__(
        self,
        username: str,
        password: str,
        token_url: str,
        transport: "OpenF1Transport",
    ) -> None:
        """
        Initialize the password auth provider.

        Args:
            username: The username for authentication.
            password: The password for authentication.
            token_url: The URL for the token endpoint.
            transport: The transport to use for token requests.

        Raises:
            OpenF1ConfigError: If username or password is empty.
        """
        if not username:
            raise OpenF1ConfigError("Username cannot be empty")
        if not password:
            raise OpenF1ConfigError("Password cannot be empty")

        self._username = username
        self._password = password
        self._token_url = token_url
        self._transport = transport
        self._token_info: TokenInfo | None = None

    def get_token(self) -> str | None:
        """
        Get the current access token.

        If no token exists or the current token is expired,
        this will attempt to obtain a new one.

        Returns:
            The access token string, or None if authentication fails.
        """
        if self._token_info is None or self._token_info.is_expired:
            try:
                self.authenticate()
            except OpenF1AuthError:
                return None

        return self._token_info.access_token if self._token_info else None

    def authenticate(self) -> TokenInfo:
        """
        Perform authentication using the password grant.

        Returns:
            The token information.

        Raises:
            OpenF1AuthError: If authentication fails.
        """
        logger.debug("Authenticating with password grant to %s", self._token_url)

        try:
            response_data = self._transport.post_form(
                url=self._token_url,
                data={
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password,
                },
            )

            self._token_info = TokenInfo.from_response(response_data)
            logger.debug("Authentication successful, token obtained")
            return self._token_info

        except Exception as e:
            logger.error("Authentication failed: %s", e)
            if isinstance(e, OpenF1AuthError):
                raise
            raise OpenF1AuthError(
                message=f"Authentication failed: {e}",
                status_code=0,
            ) from e

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with a valid token.

        Returns:
            True if a valid (non-expired) token exists.
        """
        return self._token_info is not None and not self._token_info.is_expired

    def clear(self) -> None:
        """Clear the stored token."""
        self._token_info = None

    @property
    def token_info(self) -> TokenInfo | None:
        """Get the current token info."""
        return self._token_info


class TokenAuthProvider(AuthProviderProtocol):
    """
    Simple token-based authentication provider.

    This provider uses a pre-existing access token without any
    automatic refresh capability. Suitable for cases where the
    token is obtained externally.
    """

    def __init__(self, access_token: str) -> None:
        """
        Initialize the token auth provider.

        Args:
            access_token: The pre-existing access token.

        Raises:
            OpenF1ConfigError: If the token is empty.
        """
        if not access_token:
            raise OpenF1ConfigError("Access token cannot be empty")

        self._access_token = access_token

    def get_token(self) -> str | None:
        """
        Get the access token.

        Returns:
            The access token string.
        """
        return self._access_token

    def authenticate(self) -> TokenInfo:
        """
        Return token info for the pre-existing token.

        Note: This doesn't perform any actual authentication,
        it just wraps the existing token.

        Returns:
            Token info containing the pre-existing token.
        """
        return TokenInfo(access_token=self._access_token)

    def is_authenticated(self) -> bool:
        """
        Check if a token is available.

        Returns:
            True (always, since we have a token).
        """
        return True

    def clear(self) -> None:
        """Clear the token (sets to empty string)."""
        self._access_token = ""

    def set_token(self, access_token: str) -> None:
        """
        Update the access token.

        Args:
            access_token: The new access token.
        """
        self._access_token = access_token


class NoAuthProvider(AuthProviderProtocol):
    """
    Null authentication provider for unauthenticated access.

    This provider is used when no authentication is configured,
    allowing access to public/historical API endpoints.
    """

    def get_token(self) -> str | None:
        """Return None (no token)."""
        return None

    def authenticate(self) -> TokenInfo:
        """
        Raise an error since authentication is not configured.

        Raises:
            OpenF1AuthError: Always, since no credentials are available.
        """
        raise OpenF1AuthError(
            message="No authentication configured",
            status_code=0,
        )

    def is_authenticated(self) -> bool:
        """Return False (not authenticated)."""
        return False

    def clear(self) -> None:
        """No-op since there's nothing to clear."""
        pass


class AuthManager:
    """
    Manages authentication for the OpenF1 client.

    This class coordinates between different authentication providers
    and handles token lifecycle management.
    """

    def __init__(self, provider: AuthProviderProtocol) -> None:
        """
        Initialize the auth manager.

        Args:
            provider: The authentication provider to use.
        """
        self._provider = provider

    @property
    def provider(self) -> AuthProviderProtocol:
        """Get the current auth provider."""
        return self._provider

    def get_token(self) -> str | None:
        """
        Get the current access token.

        Returns:
            The access token, or None if not authenticated.
        """
        return self._provider.get_token()

    def authenticate(self) -> TokenInfo:
        """
        Perform authentication.

        Returns:
            The token information.

        Raises:
            OpenF1AuthError: If authentication fails.
        """
        return self._provider.authenticate()

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            True if authenticated with a valid token.
        """
        return self._provider.is_authenticated()

    def clear(self) -> None:
        """Clear any stored authentication state."""
        self._provider.clear()

    def ensure_authenticated(self) -> str:
        """
        Ensure the client is authenticated and return the token.

        If not currently authenticated, this will attempt to authenticate.

        Returns:
            The access token.

        Raises:
            OpenF1AuthError: If authentication fails.
        """
        token = self.get_token()
        if token is None:
            token_info = self.authenticate()
            token = token_info.access_token
        return token
