"""
OpenF1 Client - Main Entry Point.

This module provides the main OpenF1Client class, which is the primary
interface for interacting with the OpenF1 API.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from openf1_client.auth import (
    AuthManager,
    NoAuthProvider,
    PasswordAuthProvider,
    TokenAuthProvider,
)
from openf1_client.config import ClientConfig
from openf1_client.endpoints import (
    CarDataEndpoint,
    DriversEndpoint,
    IntervalsEndpoint,
    LapsEndpoint,
    LocationEndpoint,
    MeetingsEndpoint,
    OvertakesEndpoint,
    PitEndpoint,
    PositionEndpoint,
    RaceControlEndpoint,
    SessionResultEndpoint,
    SessionsEndpoint,
    StartingGridEndpoint,
    StintsEndpoint,
    TeamRadioEndpoint,
    WeatherEndpoint,
)
from openf1_client.http_client import OpenF1Transport, SyncHTTPClient


logger = logging.getLogger("openf1_client")


class OpenF1Client:
    """
    Main client for interacting with the OpenF1 API.

    The OpenF1Client provides a clean, Pythonic interface to all OpenF1
    API endpoints with full typing support and automatic authentication
    handling.

    Attributes:
        car_data: Endpoint for car telemetry data.
        drivers: Endpoint for driver information.
        intervals: Endpoint for gap/interval data.
        laps: Endpoint for lap timing data.
        location: Endpoint for car position data.
        meetings: Endpoint for meeting (Grand Prix) data.
        overtakes: Endpoint for overtaking events (beta).
        pit: Endpoint for pit stop data.
        position: Endpoint for driver position data.
        race_control: Endpoint for race control messages.
        sessions: Endpoint for session data.
        session_result: Endpoint for session results (beta).
        starting_grid: Endpoint for starting grid data (beta).
        stints: Endpoint for stint data.
        team_radio: Endpoint for team radio communications.
        weather: Endpoint for weather data.

    Example:
        Basic unauthenticated usage:

        >>> from openf1_client import OpenF1Client
        >>> client = OpenF1Client()
        >>> laps = client.laps.list(session_key=9161, driver_number=63)

        Authenticated usage:

        >>> client = OpenF1Client(
        ...     username="user@example.com",
        ...     password="secret",
        ... )
        >>> # Client will automatically authenticate when needed

        Using a pre-existing token:

        >>> client = OpenF1Client(access_token="your_token_here")

        With custom configuration:

        >>> client = OpenF1Client(
        ...     timeout=60.0,
        ...     max_retries=5,
        ... )
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        base_url: str | None = None,
        timeout: float | tuple[float, float] | None = None,
        max_retries: int | None = None,
        default_format: Literal["json", "csv"] | None = None,
        verify_ssl: bool = True,
        **extra_config: Any,
    ) -> None:
        """
        Initialize the OpenF1 client.

        Args:
            username: Username for OAuth2 authentication (optional).
            password: Password for OAuth2 authentication (optional).
            access_token: Pre-existing access token (optional).
            base_url: Override the default API base URL.
            timeout: Request timeout in seconds, or (connect, read) tuple.
            max_retries: Maximum retry attempts for failed requests.
            default_format: Default response format ("json" or "csv").
            verify_ssl: Whether to verify SSL certificates.
            **extra_config: Additional configuration options.

        Raises:
            OpenF1ConfigError: If configuration is invalid.
        """
        # Build configuration
        config_kwargs: dict[str, Any] = {}
        if username is not None:
            config_kwargs["username"] = username
        if password is not None:
            config_kwargs["password"] = password
        if access_token is not None:
            config_kwargs["access_token"] = access_token
        if base_url is not None:
            config_kwargs["base_url"] = base_url
        if timeout is not None:
            config_kwargs["timeout"] = timeout
        if max_retries is not None:
            config_kwargs["max_retries"] = max_retries
        if default_format is not None:
            config_kwargs["default_format"] = default_format
        config_kwargs["verify_ssl"] = verify_ssl
        config_kwargs.update(extra_config)

        self._config = ClientConfig(**config_kwargs)

        # Initialize HTTP client and transport
        self._http_client = SyncHTTPClient(self._config)
        self._transport = OpenF1Transport(self._http_client, self._config)

        # Initialize authentication
        self._auth_manager = self._create_auth_manager()

        # If we have credentials or a token, update the config with the token
        if self._config.has_credentials:
            self._setup_authenticated_client()

        # Initialize endpoints (lazily)
        self._car_data: CarDataEndpoint | None = None
        self._drivers: DriversEndpoint | None = None
        self._intervals: IntervalsEndpoint | None = None
        self._laps: LapsEndpoint | None = None
        self._location: LocationEndpoint | None = None
        self._meetings: MeetingsEndpoint | None = None
        self._overtakes: OvertakesEndpoint | None = None
        self._pit: PitEndpoint | None = None
        self._position: PositionEndpoint | None = None
        self._race_control: RaceControlEndpoint | None = None
        self._sessions: SessionsEndpoint | None = None
        self._session_result: SessionResultEndpoint | None = None
        self._starting_grid: StartingGridEndpoint | None = None
        self._stints: StintsEndpoint | None = None
        self._team_radio: TeamRadioEndpoint | None = None
        self._weather: WeatherEndpoint | None = None

    def _create_auth_manager(self) -> AuthManager:
        """Create the appropriate auth manager based on configuration."""
        provider: TokenAuthProvider | PasswordAuthProvider | NoAuthProvider
        if self._config.access_token:
            provider = TokenAuthProvider(self._config.access_token)
        elif self._config.has_credentials:
            provider = PasswordAuthProvider(
                username=self._config.username,  # type: ignore
                password=self._config.password,  # type: ignore
                token_url=self._config.token_url,
                transport=self._transport,
            )
        else:
            provider = NoAuthProvider()

        return AuthManager(provider)

    def _setup_authenticated_client(self) -> None:
        """Set up authentication and update the HTTP client with the token."""
        if self._config.has_credentials and not self._config.has_token:
            try:
                token_info = self._auth_manager.authenticate()
                # Update config with the new token
                self._config = self._config.with_token(token_info.access_token)
                # Recreate HTTP client with new config
                self._http_client.close()
                self._http_client = SyncHTTPClient(self._config)
                self._transport = OpenF1Transport(self._http_client, self._config)
                logger.debug("Authentication successful, client updated with token")
            except Exception as e:
                logger.warning("Failed to authenticate: %s", e)

    @property
    def config(self) -> ClientConfig:
        """Get the client configuration."""
        return self._config

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._auth_manager.is_authenticated()

    def authenticate(self) -> None:
        """
        Explicitly authenticate the client.

        This is typically called automatically when needed, but can be
        called manually to pre-authenticate before making requests.

        Raises:
            OpenF1AuthError: If authentication fails.
            OpenF1ConfigError: If no credentials are configured.
        """
        self._setup_authenticated_client()

    # Endpoint properties (lazy initialization)

    @property
    def car_data(self) -> CarDataEndpoint:
        """Access the car telemetry data endpoint."""
        if self._car_data is None:
            self._car_data = CarDataEndpoint(self._transport)
        return self._car_data

    @property
    def drivers(self) -> DriversEndpoint:
        """Access the drivers endpoint."""
        if self._drivers is None:
            self._drivers = DriversEndpoint(self._transport)
        return self._drivers

    @property
    def intervals(self) -> IntervalsEndpoint:
        """Access the intervals/gap data endpoint."""
        if self._intervals is None:
            self._intervals = IntervalsEndpoint(self._transport)
        return self._intervals

    @property
    def laps(self) -> LapsEndpoint:
        """Access the lap timing data endpoint."""
        if self._laps is None:
            self._laps = LapsEndpoint(self._transport)
        return self._laps

    @property
    def location(self) -> LocationEndpoint:
        """Access the car location data endpoint."""
        if self._location is None:
            self._location = LocationEndpoint(self._transport)
        return self._location

    @property
    def meetings(self) -> MeetingsEndpoint:
        """Access the meetings (Grand Prix) endpoint."""
        if self._meetings is None:
            self._meetings = MeetingsEndpoint(self._transport)
        return self._meetings

    @property
    def overtakes(self) -> OvertakesEndpoint:
        """Access the overtakes endpoint (beta)."""
        if self._overtakes is None:
            self._overtakes = OvertakesEndpoint(self._transport)
        return self._overtakes

    @property
    def pit(self) -> PitEndpoint:
        """Access the pit stop data endpoint."""
        if self._pit is None:
            self._pit = PitEndpoint(self._transport)
        return self._pit

    @property
    def position(self) -> PositionEndpoint:
        """Access the driver position data endpoint."""
        if self._position is None:
            self._position = PositionEndpoint(self._transport)
        return self._position

    @property
    def race_control(self) -> RaceControlEndpoint:
        """Access the race control messages endpoint."""
        if self._race_control is None:
            self._race_control = RaceControlEndpoint(self._transport)
        return self._race_control

    @property
    def sessions(self) -> SessionsEndpoint:
        """Access the sessions endpoint."""
        if self._sessions is None:
            self._sessions = SessionsEndpoint(self._transport)
        return self._sessions

    @property
    def session_result(self) -> SessionResultEndpoint:
        """Access the session results endpoint (beta)."""
        if self._session_result is None:
            self._session_result = SessionResultEndpoint(self._transport)
        return self._session_result

    @property
    def starting_grid(self) -> StartingGridEndpoint:
        """Access the starting grid endpoint (beta)."""
        if self._starting_grid is None:
            self._starting_grid = StartingGridEndpoint(self._transport)
        return self._starting_grid

    @property
    def stints(self) -> StintsEndpoint:
        """Access the stints data endpoint."""
        if self._stints is None:
            self._stints = StintsEndpoint(self._transport)
        return self._stints

    @property
    def team_radio(self) -> TeamRadioEndpoint:
        """Access the team radio endpoint."""
        if self._team_radio is None:
            self._team_radio = TeamRadioEndpoint(self._transport)
        return self._team_radio

    @property
    def weather(self) -> WeatherEndpoint:
        """Access the weather data endpoint."""
        if self._weather is None:
            self._weather = WeatherEndpoint(self._transport)
        return self._weather

    def close(self) -> None:
        """
        Close the client and release resources.

        Should be called when the client is no longer needed to properly
        clean up HTTP connections.
        """
        self._transport.close()

    def __enter__(self) -> "OpenF1Client":
        """Enter the context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context manager and close the client."""
        self.close()

    def __repr__(self) -> str:
        """Return string representation of the client."""
        auth_status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"OpenF1Client(base_url={self._config.base_url!r}, {auth_status})"
