"""
Intervals Endpoint.

Provides access to gap and interval data between drivers.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Interval
from openf1_client.utils import FilterValue


class IntervalsEndpoint(BaseEndpoint[Interval]):
    """
    Endpoint for interval/gap data.

    Interval data shows the time gap to the car ahead and to the
    race leader. Data is updated approximately every 4 seconds.

    Example:
        >>> # Get intervals for a driver
        >>> intervals = client.intervals.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )

        >>> # Get very close intervals (within 0.5 seconds)
        >>> close_battles = client.intervals.list(
        ...     session_key=9161,
        ...     interval={"<": 0.5},
        ... )
    """

    _endpoint = "intervals"
    _model_class = Interval

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        gap_to_leader: FilterValue | None = None,
        interval: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Interval]:
        """
        Fetch interval data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            gap_to_leader: Filter by gap to P1 (supports comparison operators).
            interval: Filter by gap to car ahead (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Interval instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            gap_to_leader=gap_to_leader,
            interval=interval,
            **extra_filters,
        )

    def get_close_battles(
        self,
        session_key: int | str,
        max_interval: float = 1.0,
    ) -> list[Interval]:
        """
        Get intervals showing close battles.

        Finds instances where the gap to the car ahead is very small,
        indicating wheel-to-wheel racing.

        Args:
            session_key: The session identifier.
            max_interval: Maximum gap in seconds (default: 1.0).

        Returns:
            List of Interval instances showing close gaps.
        """
        return self.list(
            session_key=session_key,
            interval={"<": max_interval},
        )
