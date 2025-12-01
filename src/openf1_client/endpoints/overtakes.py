"""
Overtakes Endpoint.

Provides access to overtaking event data (beta endpoint).
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Overtake
from openf1_client.utils import FilterValue


class OvertakesEndpoint(BaseEndpoint[Overtake]):
    """
    Endpoint for overtaking data (beta).

    Records passing maneuvers between drivers during race sessions.

    Note: This is a beta endpoint and may have limited data availability.
    Overtake data is typically only available for race sessions.

    Example:
        >>> # Get all overtakes in a race
        >>> overtakes = client.overtakes.list(session_key=9161)

        >>> # Get overtakes by a specific driver
        >>> driver_overtakes = client.overtakes.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )
    """

    _endpoint = "overtakes"
    _model_class = Overtake

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        lap_number: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Overtake]:
        """
        Fetch overtake data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by overtaking driver.
            date: Filter by timestamp (supports comparison operators).
            lap_number: Filter by lap number (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Overtake instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            lap_number=lap_number,
            **extra_filters,
        )

    def get_driver_overtakes(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[Overtake]:
        """
        Get all overtakes made by a specific driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of Overtake instances by the driver.
        """
        return self.list(session_key=session_key, driver_number=driver_number)

    def count_overtakes(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> int:
        """
        Count the number of overtakes.

        Args:
            session_key: The session identifier.
            driver_number: Optional driver number to filter by.

        Returns:
            Number of overtakes.
        """
        return len(self.list(session_key=session_key, driver_number=driver_number))
