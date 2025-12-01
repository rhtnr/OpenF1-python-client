"""Tests for the main OpenF1Client class."""

import pytest
import responses

from openf1_client import OpenF1Client
from openf1_client.config import DEFAULT_BASE_URL
from openf1_client.errors import (
    OpenF1AuthError,
    OpenF1NotFoundError,
    OpenF1RateLimitError,
    OpenF1ServerError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_default_initialization(self) -> None:
        """Test default client initialization."""
        client = OpenF1Client()

        assert client.config.base_url == DEFAULT_BASE_URL
        assert client.is_authenticated is False
        client.close()

    def test_with_custom_config(self) -> None:
        """Test client with custom configuration."""
        client = OpenF1Client(
            timeout=60.0,
            max_retries=5,
        )

        assert client.config.timeout == 60.0
        assert client.config.max_retries == 5
        client.close()

    def test_with_access_token(self) -> None:
        """Test client with pre-existing token."""
        client = OpenF1Client(access_token="test_token")

        assert client.is_authenticated is True
        assert client.config.access_token == "test_token"
        client.close()

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with OpenF1Client() as client:
            assert client is not None

    def test_repr(self) -> None:
        """Test client string representation."""
        client = OpenF1Client()
        repr_str = repr(client)

        assert "OpenF1Client" in repr_str
        assert "unauthenticated" in repr_str
        client.close()


class TestClientEndpoints:
    """Tests for client endpoint properties."""

    def test_endpoints_initialized(self) -> None:
        """Test that all endpoints are accessible."""
        client = OpenF1Client()

        # Access each endpoint to trigger lazy initialization
        assert client.car_data is not None
        assert client.drivers is not None
        assert client.intervals is not None
        assert client.laps is not None
        assert client.location is not None
        assert client.meetings is not None
        assert client.overtakes is not None
        assert client.pit is not None
        assert client.position is not None
        assert client.race_control is not None
        assert client.sessions is not None
        assert client.session_result is not None
        assert client.starting_grid is not None
        assert client.stints is not None
        assert client.team_radio is not None
        assert client.weather is not None

        client.close()

    def test_endpoints_reuse_instance(self) -> None:
        """Test that endpoint properties return same instance."""
        client = OpenF1Client()

        laps1 = client.laps
        laps2 = client.laps

        assert laps1 is laps2
        client.close()


@responses.activate
class TestClientRequests:
    """Tests for client HTTP requests using mocked responses."""

    def test_fetch_laps(self) -> None:
        """Test fetching lap data."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/laps",
            json=[
                {
                    "session_key": 9161,
                    "driver_number": 63,
                    "lap_number": 1,
                    "lap_duration": 95.123,
                },
                {
                    "session_key": 9161,
                    "driver_number": 63,
                    "lap_number": 2,
                    "lap_duration": 92.456,
                },
            ],
            status=200,
        )

        with OpenF1Client() as client:
            laps = client.laps.list(session_key=9161, driver_number=63)

        assert len(laps) == 2
        assert laps[0].lap_number == 1
        assert laps[0].lap_duration == 95.123
        assert laps[1].lap_number == 2

    def test_fetch_drivers(self) -> None:
        """Test fetching driver data."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/drivers",
            json=[
                {
                    "driver_number": 1,
                    "full_name": "Max Verstappen",
                    "name_acronym": "VER",
                    "team_name": "Red Bull Racing",
                },
            ],
            status=200,
        )

        with OpenF1Client() as client:
            drivers = client.drivers.list(session_key=9158)

        assert len(drivers) == 1
        assert drivers[0].driver_number == 1
        assert drivers[0].full_name == "Max Verstappen"
        assert drivers[0].name_acronym == "VER"

    def test_fetch_with_filter_operators(self) -> None:
        """Test fetching with comparison operators."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/car_data",
            json=[
                {"speed": 320, "driver_number": 55},
                {"speed": 318, "driver_number": 55},
            ],
            status=200,
        )

        with OpenF1Client() as client:
            car_data = client.car_data.list(
                session_key=9159,
                driver_number=55,
                speed={">=": 315},
            )

        assert len(car_data) == 2
        # Verify the request was made with correct params
        assert "speed%3E%3D=315" in responses.calls[0].request.url

    def test_404_error(self) -> None:
        """Test handling of 404 error."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/sessions",
            json={"error": "Not found"},
            status=404,
        )

        with OpenF1Client() as client:
            with pytest.raises(OpenF1NotFoundError):
                client.sessions.list(session_key=99999)

    def test_429_rate_limit(self) -> None:
        """Test handling of rate limit error."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/car_data",
            json={"error": "Rate limited"},
            status=429,
            headers={"Retry-After": "60"},
        )

        with OpenF1Client() as client:
            with pytest.raises(OpenF1RateLimitError) as exc:
                client.car_data.list(session_key=9161)

        assert exc.value.retry_after == 60

    def test_500_server_error(self) -> None:
        """Test handling of server error."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/weather",
            json={"error": "Internal error"},
            status=500,
        )

        with OpenF1Client() as client:
            with pytest.raises(OpenF1ServerError):
                client.weather.list(session_key=9161)

    def test_fetch_first(self) -> None:
        """Test fetching first matching record."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/drivers",
            json=[
                {
                    "driver_number": 1,
                    "full_name": "Max Verstappen",
                },
            ],
            status=200,
        )

        with OpenF1Client() as client:
            driver = client.drivers.first(session_key=9158, driver_number=1)

        assert driver is not None
        assert driver.driver_number == 1

    def test_fetch_first_empty(self) -> None:
        """Test fetching first with no results."""
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/drivers",
            json=[],
            status=200,
        )

        with OpenF1Client() as client:
            driver = client.drivers.first(session_key=9158, driver_number=999)

        assert driver is None

    def test_fetch_csv(self) -> None:
        """Test fetching CSV data."""
        csv_response = "driver_number,lap_number\n63,1\n63,2"
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/laps",
            body=csv_response,
            status=200,
            content_type="text/csv",
        )

        with OpenF1Client() as client:
            csv_data = client.laps.list_csv(session_key=9161, driver_number=63)

        assert "driver_number,lap_number" in csv_data
        assert "csv=true" in responses.calls[0].request.url


@responses.activate
class TestAuthentication:
    """Tests for authentication functionality."""

    def test_auth_with_credentials(self) -> None:
        """Test authentication with username/password."""
        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://api.openf1.org/token",
            json={
                "access_token": "test_access_token",
                "token_type": "bearer",
                "expires_in": 3600,
            },
            status=200,
        )

        # Mock a data endpoint
        responses.add(
            responses.GET,
            f"{DEFAULT_BASE_URL}/sessions",
            json=[{"session_key": 9161, "session_name": "Race"}],
            status=200,
        )

        client = OpenF1Client(
            username="test@example.com",
            password="secret123",
        )

        try:
            sessions = client.sessions.list(session_key="latest")
            assert len(sessions) == 1

            # Verify auth header was used
            assert "Bearer" in responses.calls[1].request.headers.get(
                "Authorization", ""
            )
        finally:
            client.close()

    def test_auth_failure(self) -> None:
        """Test handling of authentication failure."""
        responses.add(
            responses.POST,
            "https://api.openf1.org/token",
            json={"error": "invalid_grant"},
            status=401,
        )

        # Should not raise during init, but auth will fail
        client = OpenF1Client(
            username="test@example.com",
            password="wrong_password",
        )

        # Auth manager should not be authenticated after failed attempt
        assert client.is_authenticated is False
        client.close()
