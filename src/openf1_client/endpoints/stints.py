"""
Stints Endpoint.

Provides access to stint (continuous driving period) data.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Stint
from openf1_client.utils import FilterValue


class StintsEndpoint(BaseEndpoint[Stint]):
    """
    Endpoint for stint data.

    A stint represents continuous track time between pit stops,
    including tyre compound and age information.

    Example:
        >>> # Get all stints for a driver
        >>> stints = client.stints.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )

        >>> for stint in stints:
        ...     print(f"Stint {stint.stint_number}: {stint.compound}, "
        ...           f"laps {stint.lap_start}-{stint.lap_end}")

        >>> # Get all soft tyre stints
        >>> soft_stints = client.stints.list(
        ...     session_key=9161,
        ...     compound="SOFT",
        ... )
    """

    _endpoint = "stints"
    _model_class = Stint

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        stint_number: FilterValue | None = None,
        lap_start: FilterValue | None = None,
        lap_end: FilterValue | None = None,
        compound: str | None = None,
        tyre_age_at_start: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Stint]:
        """
        Fetch stint data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            stint_number: Filter by stint number (supports comparisons).
            lap_start: Filter by first lap (supports comparison operators).
            lap_end: Filter by last lap (supports comparison operators).
            compound: Filter by tyre compound (SOFT, MEDIUM, HARD, etc.).
            tyre_age_at_start: Filter by tyre age at stint start.
            **extra_filters: Additional filter parameters.

        Returns:
            List of Stint instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            stint_number=stint_number,
            lap_start=lap_start,
            lap_end=lap_end,
            compound=compound,
            tyre_age_at_start=tyre_age_at_start,
            **extra_filters,
        )

    def get_driver_stints(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[Stint]:
        """
        Get all stints for a specific driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of Stint instances for the driver, ordered by stint number.
        """
        stints = self.list(session_key=session_key, driver_number=driver_number)
        return sorted(stints, key=lambda s: s.stint_number or 0)

    def get_by_compound(
        self,
        session_key: int | str,
        compound: str,
    ) -> list[Stint]:
        """
        Get all stints using a specific compound.

        Args:
            session_key: The session identifier.
            compound: Tyre compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET).

        Returns:
            List of Stint instances using that compound.
        """
        return self.list(session_key=session_key, compound=compound.upper())

    def get_tyre_strategy(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[str]:
        """
        Get the tyre strategy (sequence of compounds) for a driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of compound names in order of use.
        """
        stints = self.get_driver_stints(session_key, driver_number)
        return [s.compound for s in stints if s.compound is not None]
