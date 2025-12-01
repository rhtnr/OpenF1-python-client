"""
Pit Endpoint.

Provides access to pit stop activity data.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Pit
from openf1_client.utils import FilterValue


class PitEndpoint(BaseEndpoint[Pit]):
    """
    Endpoint for pit stop data.

    Records when drivers enter and exit the pit lane,
    along with pit stop duration.

    Example:
        >>> # Get all pit stops in a race
        >>> pit_stops = client.pit.list(session_key=9161)

        >>> # Get pit stops for a specific driver
        >>> driver_pits = client.pit.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )

        >>> # Get fast pit stops under 25 seconds
        >>> fast_stops = client.pit.list(
        ...     session_key=9161,
        ...     pit_duration={"<": 25.0},
        ... )
    """

    _endpoint = "pit"
    _model_class = Pit

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        lap_number: FilterValue | None = None,
        pit_duration: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Pit]:
        """
        Fetch pit stop data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            lap_number: Filter by lap number (supports comparison operators).
            pit_duration: Filter by pit duration in seconds.
            **extra_filters: Additional filter parameters.

        Returns:
            List of Pit instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            lap_number=lap_number,
            pit_duration=pit_duration,
            **extra_filters,
        )

    def get_driver_pit_stops(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[Pit]:
        """
        Get all pit stops for a specific driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of Pit instances for the driver.
        """
        return self.list(session_key=session_key, driver_number=driver_number)

    def get_fastest_pit_stop(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> Pit | None:
        """
        Get the fastest pit stop.

        Args:
            session_key: The session identifier.
            driver_number: Optional driver number to filter by.

        Returns:
            The Pit with shortest duration, or None if no pit stops.
        """
        pit_stops = self.list(
            session_key=session_key,
            driver_number=driver_number,
        )

        valid_stops = [p for p in pit_stops if p.pit_duration is not None]
        if not valid_stops:
            return None

        return min(valid_stops, key=lambda x: x.pit_duration or float("inf"))

    def count_pit_stops(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> int:
        """
        Count the number of pit stops for a driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            Number of pit stops.
        """
        return len(self.get_driver_pit_stops(session_key, driver_number))
