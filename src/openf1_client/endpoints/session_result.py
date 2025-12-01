"""
Session Result Endpoint.

Provides access to final session results (beta endpoint).
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import SessionResult
from openf1_client.utils import FilterValue


class SessionResultEndpoint(BaseEndpoint[SessionResult]):
    """
    Endpoint for session results (beta).

    Contains the final standings and classification for a session.

    Note: This is a beta endpoint and may have limited data availability.

    Example:
        >>> # Get race results
        >>> results = client.session_result.list(session_key=9161)

        >>> # Sort by position
        >>> sorted_results = sorted(results, key=lambda r: r.position or 999)
        >>> for r in sorted_results:
        ...     print(f"P{r.position}: Driver #{r.driver_number}")
    """

    _endpoint = "session_result"
    _model_class = SessionResult

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        position: FilterValue | None = None,
        points: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[SessionResult]:
        """
        Fetch session result data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            position: Filter by final position (supports comparison operators).
            points: Filter by points awarded (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of SessionResult instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            position=position,
            points=points,
            **extra_filters,
        )

    def get_podium(self, session_key: int | str) -> list[SessionResult]:
        """
        Get podium finishers (P1-P3).

        Args:
            session_key: The session identifier.

        Returns:
            List of SessionResult instances for top 3.
        """
        results = self.list(session_key=session_key, position={"<=": 3})
        return sorted(results, key=lambda r: r.position or 999)

    def get_winner(self, session_key: int | str) -> SessionResult | None:
        """
        Get the session winner.

        Args:
            session_key: The session identifier.

        Returns:
            The P1 SessionResult, or None if not found.
        """
        return self.first(session_key=session_key, position=1)

    def get_points_finishers(self, session_key: int | str) -> list[SessionResult]:
        """
        Get all drivers who scored points (typically P1-P10).

        Args:
            session_key: The session identifier.

        Returns:
            List of SessionResult instances for points finishers.
        """
        return self.list(session_key=session_key, points={">": 0})
