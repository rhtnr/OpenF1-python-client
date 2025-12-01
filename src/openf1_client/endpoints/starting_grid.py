"""
Starting Grid Endpoint.

Provides access to starting grid positions (beta endpoint).
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import StartingGrid
from openf1_client.utils import FilterValue


class StartingGridEndpoint(BaseEndpoint[StartingGrid]):
    """
    Endpoint for starting grid data (beta).

    Contains the grid positions at the start of a race or sprint.

    Note: This is a beta endpoint and may have limited data availability.

    Example:
        >>> # Get starting grid for a race
        >>> grid = client.starting_grid.list(session_key=9161)

        >>> # Sort by position
        >>> sorted_grid = sorted(grid, key=lambda g: g.position or 999)
        >>> for g in sorted_grid:
        ...     print(f"P{g.position}: Driver #{g.driver_number}")
    """

    _endpoint = "starting_grid"
    _model_class = StartingGrid

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        position: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[StartingGrid]:
        """
        Fetch starting grid data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            position: Filter by grid position (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of StartingGrid instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            position=position,
            **extra_filters,
        )

    def get_pole_sitter(self, session_key: int | str) -> StartingGrid | None:
        """
        Get the pole position driver.

        Args:
            session_key: The session identifier.

        Returns:
            The P1 StartingGrid entry, or None if not found.
        """
        return self.first(session_key=session_key, position=1)

    def get_front_row(self, session_key: int | str) -> list[StartingGrid]:
        """
        Get front row starters (P1-P2).

        Args:
            session_key: The session identifier.

        Returns:
            List of StartingGrid instances for front row.
        """
        grid = self.list(session_key=session_key, position={"<=": 2})
        return sorted(grid, key=lambda g: g.position or 999)

    def get_driver_grid_position(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> int | None:
        """
        Get a driver's grid position.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            The grid position, or None if not found.
        """
        entry = self.first(session_key=session_key, driver_number=driver_number)
        return entry.position if entry else None

    def get_sorted_grid(self, session_key: int | str) -> list[StartingGrid]:
        """
        Get the full grid sorted by position.

        Args:
            session_key: The session identifier.

        Returns:
            List of StartingGrid instances sorted by position.
        """
        grid = self.list(session_key=session_key)
        return sorted(grid, key=lambda g: g.position or 999)
