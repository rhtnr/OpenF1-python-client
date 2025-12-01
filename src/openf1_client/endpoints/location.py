"""
Location Endpoint.

Provides access to car position data on the circuit.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Location
from openf1_client.utils import FilterValue


class LocationEndpoint(BaseEndpoint[Location]):
    """
    Endpoint for car location/position data.

    Location data provides X, Y, Z coordinates representing each car's
    position on the track surface. Data is sampled at approximately 3.7 Hz.

    Example:
        >>> # Get location data for a driver during a specific time
        >>> locations = client.location.list(
        ...     session_key=9161,
        ...     driver_number=81,
        ...     date={">": "2023-09-16T13:03:35.200", "<": "2023-09-16T13:03:35.800"},
        ... )

        >>> for loc in locations:
        ...     print(f"Position: ({loc.x}, {loc.y}, {loc.z})")
    """

    _endpoint = "location"
    _model_class = Location

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        x: FilterValue | None = None,
        y: FilterValue | None = None,
        z: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Location]:
        """
        Fetch car location data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            x: Filter by X coordinate (supports comparison operators).
            y: Filter by Y coordinate (supports comparison operators).
            z: Filter by Z coordinate/elevation (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Location instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            x=x,
            y=y,
            z=z,
            **extra_filters,
        )

    def get_track_positions(
        self,
        session_key: int | str,
        driver_number: int,
        start_time: str,
        end_time: str,
    ) -> list[Location]:
        """
        Get track positions for a time window.

        Useful for reconstructing a driver's path around the track
        during a specific time period.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.
            start_time: Start time in ISO 8601 format.
            end_time: End time in ISO 8601 format.

        Returns:
            List of Location instances for the time window.
        """
        return self.list(
            session_key=session_key,
            driver_number=driver_number,
            date={">": start_time, "<": end_time},
        )
