"""
Race Control Endpoint.

Provides access to race control messages and events.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import RaceControl
from openf1_client.utils import FilterValue


class RaceControlEndpoint(BaseEndpoint[RaceControl]):
    """
    Endpoint for race control messages.

    Race control data includes flags, safety car deployments,
    incidents, and other official race communications.

    Example:
        >>> # Get all race control messages for a session
        >>> messages = client.race_control.list(session_key=9161)

        >>> # Get yellow flag events
        >>> yellow_flags = client.race_control.list(
        ...     session_key=9161,
        ...     flag="YELLOW",
        ... )

        >>> # Get messages for a specific driver
        >>> driver_messages = client.race_control.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )
    """

    _endpoint = "race_control"
    _model_class = RaceControl

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        lap_number: FilterValue | None = None,
        category: str | None = None,
        flag: str | None = None,
        scope: str | None = None,
        sector: int | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[RaceControl]:
        """
        Fetch race control messages.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by affected driver.
            date: Filter by timestamp (supports comparison operators).
            lap_number: Filter by lap number (supports comparison operators).
            category: Filter by message category.
            flag: Filter by flag type (GREEN, YELLOW, RED, CHEQUERED, etc.).
            scope: Filter by flag scope (Track, Sector, Driver).
            sector: Filter by affected sector number.
            **extra_filters: Additional filter parameters.

        Returns:
            List of RaceControl instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            lap_number=lap_number,
            category=category,
            flag=flag,
            scope=scope,
            sector=sector,
            **extra_filters,
        )

    def get_flags(
        self,
        session_key: int | str,
        flag: str | None = None,
    ) -> list[RaceControl]:
        """
        Get flag events.

        Args:
            session_key: The session identifier.
            flag: Optional flag type to filter (e.g., "YELLOW", "RED").

        Returns:
            List of flag RaceControl instances.
        """
        messages = self.list(session_key=session_key, flag=flag)
        return [m for m in messages if m.flag is not None]

    def get_safety_car_events(
        self,
        session_key: int | str,
    ) -> list[RaceControl]:
        """
        Get safety car related events.

        Args:
            session_key: The session identifier.

        Returns:
            List of safety car RaceControl instances.
        """
        messages = self.list(session_key=session_key)
        return [
            m
            for m in messages
            if m.message and ("SAFETY CAR" in m.message.upper() or "VSC" in m.message.upper())
        ]

    def get_driver_incidents(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[RaceControl]:
        """
        Get incidents involving a specific driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of RaceControl instances involving the driver.
        """
        return self.list(session_key=session_key, driver_number=driver_number)
