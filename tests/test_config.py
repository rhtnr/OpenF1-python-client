"""Tests for the configuration module."""

import pytest

from openf1_client.config import ClientConfig, DEFAULT_BASE_URL
from openf1_client.errors import OpenF1ConfigError


class TestClientConfig:
    """Tests for ClientConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ClientConfig()

        assert config.base_url == DEFAULT_BASE_URL
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.username is None
        assert config.password is None
        assert config.access_token is None
        assert config.default_format == "json"
        assert config.verify_ssl is True

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = ClientConfig(
            base_url="https://custom.api.com/v1",
            timeout=60.0,
            max_retries=5,
            default_format="csv",
        )

        assert config.base_url == "https://custom.api.com/v1"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.default_format == "csv"

    def test_auth_credentials(self) -> None:
        """Test authentication credential configuration."""
        config = ClientConfig(
            username="user@example.com",
            password="secret123",
        )

        assert config.has_credentials is True
        assert config.has_token is False
        assert config.is_authenticated is True

    def test_auth_token(self) -> None:
        """Test access token configuration."""
        config = ClientConfig(access_token="my_token_123")

        assert config.has_credentials is False
        assert config.has_token is True
        assert config.is_authenticated is True

    def test_no_auth(self) -> None:
        """Test unauthenticated configuration."""
        config = ClientConfig()

        assert config.has_credentials is False
        assert config.has_token is False
        assert config.is_authenticated is False

    def test_invalid_base_url_empty(self) -> None:
        """Test that empty base URL raises error."""
        with pytest.raises(OpenF1ConfigError, match="cannot be empty"):
            ClientConfig(base_url="")

    def test_invalid_base_url_no_scheme(self) -> None:
        """Test that base URL without scheme raises error."""
        with pytest.raises(OpenF1ConfigError, match="must start with http"):
            ClientConfig(base_url="api.openf1.org")

    def test_invalid_timeout_negative(self) -> None:
        """Test that negative timeout raises error."""
        with pytest.raises(OpenF1ConfigError, match="must be positive"):
            ClientConfig(timeout=-1.0)

    def test_invalid_timeout_tuple(self) -> None:
        """Test that invalid timeout tuple raises error."""
        with pytest.raises(OpenF1ConfigError, match="exactly 2 values"):
            ClientConfig(timeout=(1.0, 2.0, 3.0))  # type: ignore

    def test_invalid_max_retries(self) -> None:
        """Test that negative max_retries raises error."""
        with pytest.raises(OpenF1ConfigError, match="cannot be negative"):
            ClientConfig(max_retries=-1)

    def test_mismatched_credentials(self) -> None:
        """Test that providing only username or password raises error."""
        with pytest.raises(OpenF1ConfigError, match="must be provided together"):
            ClientConfig(username="user@example.com")

        with pytest.raises(OpenF1ConfigError, match="must be provided together"):
            ClientConfig(password="secret")

    def test_invalid_format(self) -> None:
        """Test that invalid format raises error."""
        with pytest.raises(OpenF1ConfigError, match="must be 'json' or 'csv'"):
            ClientConfig(default_format="xml")  # type: ignore

    def test_timeout_tuple(self) -> None:
        """Test tuple timeout configuration."""
        config = ClientConfig(timeout=(5.0, 30.0))

        assert config.get_connect_timeout() == 5.0
        assert config.get_read_timeout() == 30.0

    def test_timeout_single(self) -> None:
        """Test single timeout value."""
        config = ClientConfig(timeout=15.0)

        assert config.get_connect_timeout() == 15.0
        assert config.get_read_timeout() == 15.0

    def test_get_headers(self) -> None:
        """Test header generation."""
        config = ClientConfig(
            extra_headers={"X-Custom": "value"}
        )
        headers = config.get_headers()

        assert "User-Agent" in headers
        assert headers["X-Custom"] == "value"

    def test_with_token(self) -> None:
        """Test creating new config with token."""
        original = ClientConfig(username="user", password="pass")
        new_config = original.with_token("new_token")

        assert original.access_token is None
        assert new_config.access_token == "new_token"
        assert new_config.username == "user"

    def test_copy(self) -> None:
        """Test config copy with updates."""
        original = ClientConfig(timeout=30.0)
        copied = original.copy(timeout=60.0)

        assert original.timeout == 30.0
        assert copied.timeout == 60.0
