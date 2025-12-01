"""
Drivers Endpoint.

Provides access to driver information for each session.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Driver
from openf1_client.utils import FilterValue


class DriversEndpoint(BaseEndpoint[Driver]):
    """
    Endpoint for driver information.

    Driver data is session-specific as drivers may change teams
    or use different numbers during testing.

    Example:
        >>> # Get all drivers in a session
        >>> drivers = client.drivers.list(session_key=9158)

        >>> # Get a specific driver
        >>> driver = client.drivers.first(
        ...     session_key=9158,
        ...     driver_number=1,
        ... )
        >>> print(f"{driver.full_name} - {driver.team_name}")
    """

    _endpoint = "drivers"
    _model_class = Driver

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        name_acronym: str | None = None,
        team_name: str | None = None,
        country_code: str | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Driver]:
        """
        Fetch driver information.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number (1-99).
            name_acronym: Filter by three-letter acronym (e.g., "VER", "HAM").
            team_name: Filter by team name.
            country_code: Filter by nationality ISO code.
            **extra_filters: Additional filter parameters.

        Returns:
            List of Driver instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            name_acronym=name_acronym,
            team_name=team_name,
            country_code=country_code,
            **extra_filters,
        )

    def get_by_number(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> Driver | None:
        """
        Get a specific driver by number.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            The Driver instance, or None if not found.
        """
        return self.first(session_key=session_key, driver_number=driver_number)

    def get_by_acronym(
        self,
        session_key: int | str,
        name_acronym: str,
    ) -> Driver | None:
        """
        Get a specific driver by acronym.

        Args:
            session_key: The session identifier.
            name_acronym: Three-letter driver acronym (e.g., "VER").

        Returns:
            The Driver instance, or None if not found.
        """
        return self.first(session_key=session_key, name_acronym=name_acronym.upper())

    def get_by_team(
        self,
        session_key: int | str,
        team_name: str,
    ) -> list[Driver]:
        """
        Get all drivers for a specific team.

        Args:
            session_key: The session identifier.
            team_name: The team name to filter by.

        Returns:
            List of Driver instances for the team.
        """
        return self.list(session_key=session_key, team_name=team_name)
