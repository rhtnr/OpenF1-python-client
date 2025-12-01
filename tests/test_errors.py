"""Tests for the error handling module."""

import pytest

from openf1_client.errors import (
    OpenF1APIError,
    OpenF1AuthError,
    OpenF1ConfigError,
    OpenF1Error,
    OpenF1NotFoundError,
    OpenF1RateLimitError,
    OpenF1ServerError,
    OpenF1TimeoutError,
    OpenF1TransportError,
    OpenF1ValidationError,
    raise_for_status,
)


class TestErrorHierarchy:
    """Tests for error class hierarchy."""

    def test_base_error(self) -> None:
        """Test base OpenF1Error."""
        error = OpenF1Error("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert isinstance(error, Exception)

    def test_config_error(self) -> None:
        """Test OpenF1ConfigError."""
        error = OpenF1ConfigError("Invalid config")
        assert isinstance(error, OpenF1Error)
        assert str(error) == "Invalid config"

    def test_transport_error(self) -> None:
        """Test OpenF1TransportError."""
        original = ConnectionError("Connection refused")
        error = OpenF1TransportError("Network error", original)

        assert isinstance(error, OpenF1Error)
        assert error.original_error is original
        assert "Connection refused" in str(error)

    def test_api_error(self) -> None:
        """Test OpenF1APIError."""
        error = OpenF1APIError(
            message="API Error",
            status_code=400,
            response_body={"error": "Bad request"},
            request_url="https://api.openf1.org/v1/test",
        )

        assert isinstance(error, OpenF1Error)
        assert error.status_code == 400
        assert error.response_body == {"error": "Bad request"}
        assert "400" in str(error)
        assert "API Error" in str(error)

    def test_auth_error(self) -> None:
        """Test OpenF1AuthError."""
        error = OpenF1AuthError(status_code=401)

        assert isinstance(error, OpenF1APIError)
        assert isinstance(error, OpenF1Error)
        assert error.status_code == 401

    def test_rate_limit_error(self) -> None:
        """Test OpenF1RateLimitError."""
        error = OpenF1RateLimitError(retry_after=60)

        assert isinstance(error, OpenF1APIError)
        assert error.status_code == 429
        assert error.retry_after == 60
        assert "60s" in str(error)

    def test_not_found_error(self) -> None:
        """Test OpenF1NotFoundError."""
        error = OpenF1NotFoundError()

        assert isinstance(error, OpenF1APIError)
        assert error.status_code == 404

    def test_server_error(self) -> None:
        """Test OpenF1ServerError."""
        error = OpenF1ServerError(status_code=503)

        assert isinstance(error, OpenF1APIError)
        assert error.status_code == 503

    def test_timeout_error(self) -> None:
        """Test OpenF1TimeoutError."""
        error = OpenF1TimeoutError(timeout=30.0)

        assert isinstance(error, OpenF1TransportError)
        assert isinstance(error, OpenF1Error)
        assert error.timeout == 30.0
        assert "30.0s" in str(error)

    def test_validation_error(self) -> None:
        """Test OpenF1ValidationError."""
        error = OpenF1ValidationError(
            message="Validation failed",
            field="speed",
            value=-1,
        )

        assert isinstance(error, OpenF1Error)
        assert error.field == "speed"
        assert error.value == -1
        assert "speed" in str(error)


class TestRaiseForStatus:
    """Tests for raise_for_status function."""

    def test_success_codes_no_raise(self) -> None:
        """Test that 2xx codes don't raise."""
        for code in [200, 201, 204]:
            raise_for_status(code)  # Should not raise

    def test_401_raises_auth_error(self) -> None:
        """Test that 401 raises OpenF1AuthError."""
        with pytest.raises(OpenF1AuthError) as exc:
            raise_for_status(401)
        assert exc.value.status_code == 401

    def test_403_raises_auth_error(self) -> None:
        """Test that 403 raises OpenF1AuthError."""
        with pytest.raises(OpenF1AuthError) as exc:
            raise_for_status(403)
        assert exc.value.status_code == 403

    def test_404_raises_not_found(self) -> None:
        """Test that 404 raises OpenF1NotFoundError."""
        with pytest.raises(OpenF1NotFoundError) as exc:
            raise_for_status(404)
        assert exc.value.status_code == 404

    def test_429_raises_rate_limit(self) -> None:
        """Test that 429 raises OpenF1RateLimitError."""
        with pytest.raises(OpenF1RateLimitError) as exc:
            raise_for_status(429, retry_after=120)
        assert exc.value.status_code == 429
        assert exc.value.retry_after == 120

    def test_500_raises_server_error(self) -> None:
        """Test that 500 raises OpenF1ServerError."""
        with pytest.raises(OpenF1ServerError) as exc:
            raise_for_status(500)
        assert exc.value.status_code == 500

    def test_502_raises_server_error(self) -> None:
        """Test that 502 raises OpenF1ServerError."""
        with pytest.raises(OpenF1ServerError) as exc:
            raise_for_status(502)
        assert exc.value.status_code == 502

    def test_503_raises_server_error(self) -> None:
        """Test that 503 raises OpenF1ServerError."""
        with pytest.raises(OpenF1ServerError) as exc:
            raise_for_status(503)
        assert exc.value.status_code == 503

    def test_400_raises_api_error(self) -> None:
        """Test that 400 raises generic OpenF1APIError."""
        with pytest.raises(OpenF1APIError) as exc:
            raise_for_status(400)
        assert exc.value.status_code == 400

    def test_includes_response_body(self) -> None:
        """Test that response body is included in error."""
        with pytest.raises(OpenF1APIError) as exc:
            raise_for_status(
                400,
                response_body={"detail": "Invalid parameter"},
                request_url="https://api.example.com/test",
            )
        assert exc.value.response_body == {"detail": "Invalid parameter"}
        assert exc.value.request_url == "https://api.example.com/test"
