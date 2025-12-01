"""
Position Endpoint.

Provides access to driver position data throughout sessions.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Position
from openf1_client.utils import FilterValue


class PositionEndpoint(BaseEndpoint[Position]):
    """
    Endpoint for driver position data.

    Tracks position changes over time, useful for visualizing
    race progression and position battles.

    Example:
        >>> # Get position history for a driver
        >>> positions = client.position.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )

        >>> # Get all drivers in P1 at any point
        >>> p1_moments = client.position.list(
        ...     session_key=9161,
        ...     position=1,
        ... )
    """

    _endpoint = "position"
    _model_class = Position

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        position: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Position]:
        """
        Fetch position data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            position: Filter by position (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Position instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            position=position,
            **extra_filters,
        )

    def get_driver_positions(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[Position]:
        """
        Get all position entries for a driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of Position instances for the driver.
        """
        return self.list(session_key=session_key, driver_number=driver_number)

    def get_position_at_time(
        self,
        session_key: int | str,
        position: int,
    ) -> list[Position]:
        """
        Get all drivers who held a specific position.

        Args:
            session_key: The session identifier.
            position: The track position to query.

        Returns:
            List of Position instances for that position.
        """
        return self.list(session_key=session_key, position=position)

    def get_leaders(self, session_key: int | str) -> list[Position]:
        """
        Get all P1 entries.

        Useful for tracking race lead changes.

        Args:
            session_key: The session identifier.

        Returns:
            List of Position instances for P1.
        """
        return self.list(session_key=session_key, position=1)
