"""
Sessions Endpoint.

Provides access to session data (practice, qualifying, race, etc.).
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Session
from openf1_client.utils import FilterValue


class SessionsEndpoint(BaseEndpoint[Session]):
    """
    Endpoint for session data.

    Sessions include practice (FP1, FP2, FP3), qualifying, sprint
    shootout, sprint race, and the main race.

    Example:
        >>> # Get all sessions for a meeting
        >>> sessions = client.sessions.list(meeting_key=1219)

        >>> # Get the latest session
        >>> session = client.sessions.first(session_key="latest")
        >>> print(f"{session.session_name} - {session.country_name}")

        >>> # Get all race sessions in a season
        >>> races = client.sessions.list(year=2023, session_name="Race")
    """

    _endpoint = "sessions"
    _model_class = Session

    def list(
        self,
        session_key: int | str | None = None,
        session_name: str | None = None,
        session_type: str | None = None,
        meeting_key: int | str | None = None,
        year: int | None = None,
        country_key: int | None = None,
        country_code: str | None = None,
        country_name: str | None = None,
        circuit_key: int | None = None,
        circuit_short_name: str | None = None,
        date_start: FilterValue | None = None,
        date_end: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Session]:
        """
        Fetch session data.

        Args:
            session_key: Filter by session ID (use "latest" for current).
            session_name: Filter by session name (e.g., "Race", "Qualifying").
            session_type: Filter by session type.
            meeting_key: Filter by meeting ID (use "latest" for current).
            year: Filter by season year.
            country_key: Filter by country identifier.
            country_code: Filter by ISO country code.
            country_name: Filter by country name.
            circuit_key: Filter by circuit identifier.
            circuit_short_name: Filter by circuit short name.
            date_start: Filter by start time (supports comparison operators).
            date_end: Filter by end time (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Session instances.
        """
        return super().list(
            session_key=session_key,
            session_name=session_name,
            session_type=session_type,
            meeting_key=meeting_key,
            year=year,
            country_key=country_key,
            country_code=country_code,
            country_name=country_name,
            circuit_key=circuit_key,
            circuit_short_name=circuit_short_name,
            date_start=date_start,
            date_end=date_end,
            **extra_filters,
        )

    def get_by_key(self, session_key: int | str) -> Session | None:
        """
        Get a specific session by key.

        Args:
            session_key: The session identifier (or "latest").

        Returns:
            The Session instance, or None if not found.
        """
        return self.first(session_key=session_key)

    def get_latest(self) -> Session | None:
        """
        Get the current/latest session.

        Returns:
            The latest Session instance, or None if not available.
        """
        return self.first(session_key="latest")

    def get_for_meeting(self, meeting_key: int | str) -> list[Session]:
        """
        Get all sessions for a meeting.

        Args:
            meeting_key: The meeting identifier (or "latest").

        Returns:
            List of Session instances for the meeting.
        """
        return self.list(meeting_key=meeting_key)

    def get_races(self, year: int | None = None) -> list[Session]:
        """
        Get all race sessions.

        Args:
            year: Optional year to filter by.

        Returns:
            List of race Session instances.
        """
        return self.list(session_name="Race", year=year)

    def get_qualifying(self, year: int | None = None) -> list[Session]:
        """
        Get all qualifying sessions.

        Args:
            year: Optional year to filter by.

        Returns:
            List of qualifying Session instances.
        """
        return self.list(session_name="Qualifying", year=year)

    def get_practice(
        self,
        meeting_key: int | str | None = None,
        practice_number: int | None = None,
    ) -> list[Session]:
        """
        Get practice sessions.

        Args:
            meeting_key: Optional meeting to filter by.
            practice_number: Optional practice number (1, 2, or 3).

        Returns:
            List of practice Session instances.
        """
        if practice_number is not None:
            session_name = f"Practice {practice_number}"
            return self.list(meeting_key=meeting_key, session_name=session_name)

        # Get all practice sessions
        sessions = self.list(meeting_key=meeting_key)
        return [s for s in sessions if s.session_name and "Practice" in s.session_name]
