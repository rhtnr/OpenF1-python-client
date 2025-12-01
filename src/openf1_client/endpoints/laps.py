"""
Laps Endpoint.

Provides access to detailed lap-by-lap timing data.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Lap
from openf1_client.utils import FilterValue


class LapsEndpoint(BaseEndpoint[Lap]):
    """
    Endpoint for lap timing data.

    Provides detailed timing information for each completed lap,
    including sector times and speed trap measurements.

    Example:
        >>> # Get all laps for a driver in a session
        >>> laps = client.laps.list(
        ...     session_key=9161,
        ...     driver_number=63,
        ... )

        >>> # Get a specific lap
        >>> lap = client.laps.first(
        ...     session_key=9161,
        ...     driver_number=63,
        ...     lap_number=8,
        ... )
        >>> print(f"Lap time: {lap.lap_duration}s")

        >>> # Get fast laps under a certain time
        >>> fast_laps = client.laps.list(
        ...     session_key=9161,
        ...     lap_duration={"<": 90.0},
        ... )
    """

    _endpoint = "laps"
    _model_class = Lap

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        lap_number: FilterValue | None = None,
        date_start: FilterValue | None = None,
        lap_duration: FilterValue | None = None,
        duration_sector_1: FilterValue | None = None,
        duration_sector_2: FilterValue | None = None,
        duration_sector_3: FilterValue | None = None,
        i1_speed: FilterValue | None = None,
        i2_speed: FilterValue | None = None,
        st_speed: FilterValue | None = None,
        is_pit_out_lap: bool | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Lap]:
        """
        Fetch lap timing data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            lap_number: Filter by lap number (supports comparison operators).
            date_start: Filter by lap start time (supports comparison operators).
            lap_duration: Filter by lap time in seconds.
            duration_sector_1: Filter by S1 time in seconds.
            duration_sector_2: Filter by S2 time in seconds.
            duration_sector_3: Filter by S3 time in seconds.
            i1_speed: Filter by intermediate 1 speed.
            i2_speed: Filter by intermediate 2 speed.
            st_speed: Filter by speed trap speed.
            is_pit_out_lap: Filter for pit out laps (True/False).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Lap instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            lap_number=lap_number,
            date_start=date_start,
            lap_duration=lap_duration,
            duration_sector_1=duration_sector_1,
            duration_sector_2=duration_sector_2,
            duration_sector_3=duration_sector_3,
            i1_speed=i1_speed,
            i2_speed=i2_speed,
            st_speed=st_speed,
            is_pit_out_lap=is_pit_out_lap,
            **extra_filters,
        )

    def get_fastest_lap(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> Lap | None:
        """
        Get the fastest lap in a session.

        Args:
            session_key: The session identifier.
            driver_number: Optional driver number to filter by.

        Returns:
            The Lap with the shortest duration, or None if no valid laps.
        """
        laps = self.list(
            session_key=session_key,
            driver_number=driver_number,
        )

        # Filter out laps without valid duration
        valid_laps = [lap for lap in laps if lap.lap_duration is not None]
        if not valid_laps:
            return None

        return min(valid_laps, key=lambda x: x.lap_duration or float("inf"))

    def get_lap(
        self,
        session_key: int | str,
        driver_number: int,
        lap_number: int,
    ) -> Lap | None:
        """
        Get a specific lap for a driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.
            lap_number: The lap number.

        Returns:
            The Lap instance, or None if not found.
        """
        return self.first(
            session_key=session_key,
            driver_number=driver_number,
            lap_number=lap_number,
        )

    def get_lap_range(
        self,
        session_key: int | str,
        driver_number: int,
        start_lap: int,
        end_lap: int,
    ) -> list[Lap]:
        """
        Get laps within a specific range.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.
            start_lap: First lap number (inclusive).
            end_lap: Last lap number (inclusive).

        Returns:
            List of Lap instances in the range.
        """
        return self.list(
            session_key=session_key,
            driver_number=driver_number,
            lap_number={">=": start_lap, "<=": end_lap},
        )

    def get_flying_laps(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[Lap]:
        """
        Get flying laps (excluding pit out laps).

        Flying laps are laps that start from a normal on-track position
        rather than exiting the pit lane.

        Args:
            session_key: The session identifier.
            driver_number: Optional driver number to filter by.

        Returns:
            List of flying Lap instances.
        """
        return self.list(
            session_key=session_key,
            driver_number=driver_number,
            is_pit_out_lap=False,
        )
