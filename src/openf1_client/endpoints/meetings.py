"""
Meetings Endpoint.

Provides access to Grand Prix weekend and testing event metadata.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Meeting
from openf1_client.utils import FilterValue


class MeetingsEndpoint(BaseEndpoint[Meeting]):
    """
    Endpoint for meeting (Grand Prix/event) data.

    A meeting represents a complete race weekend or testing event,
    encompassing all sessions at a single venue.

    Example:
        >>> # Get all meetings for a season
        >>> meetings = client.meetings.list(year=2023)

        >>> # Get the latest meeting
        >>> meeting = client.meetings.first(meeting_key="latest")
        >>> print(f"{meeting.meeting_name} - {meeting.country_name}")

        >>> # Get a specific Grand Prix
        >>> monaco = client.meetings.first(meeting_name="Monaco Grand Prix")
    """

    _endpoint = "meetings"
    _model_class = Meeting

    def list(
        self,
        meeting_key: int | str | None = None,
        meeting_name: str | None = None,
        year: int | None = None,
        country_key: int | None = None,
        country_code: str | None = None,
        country_name: str | None = None,
        circuit_key: int | None = None,
        circuit_short_name: str | None = None,
        date_start: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Meeting]:
        """
        Fetch meeting data.

        Args:
            meeting_key: Filter by meeting ID (use "latest" for current).
            meeting_name: Filter by meeting name.
            year: Filter by season year.
            country_key: Filter by country identifier.
            country_code: Filter by ISO country code.
            country_name: Filter by country name.
            circuit_key: Filter by circuit identifier.
            circuit_short_name: Filter by circuit short name.
            date_start: Filter by start date (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Meeting instances.
        """
        return super().list(
            meeting_key=meeting_key,
            meeting_name=meeting_name,
            year=year,
            country_key=country_key,
            country_code=country_code,
            country_name=country_name,
            circuit_key=circuit_key,
            circuit_short_name=circuit_short_name,
            date_start=date_start,
            **extra_filters,
        )

    def get_by_key(self, meeting_key: int | str) -> Meeting | None:
        """
        Get a specific meeting by key.

        Args:
            meeting_key: The meeting identifier (or "latest").

        Returns:
            The Meeting instance, or None if not found.
        """
        return self.first(meeting_key=meeting_key)

    def get_latest(self) -> Meeting | None:
        """
        Get the current/latest meeting.

        Returns:
            The latest Meeting instance, or None if not available.
        """
        return self.first(meeting_key="latest")

    def get_by_season(self, year: int) -> list[Meeting]:
        """
        Get all meetings for a season.

        Args:
            year: The season year.

        Returns:
            List of Meeting instances for the season.
        """
        return self.list(year=year)

    def get_by_country(self, country_name: str) -> list[Meeting]:
        """
        Get meetings in a specific country.

        Args:
            country_name: The country name.

        Returns:
            List of Meeting instances in that country.
        """
        return self.list(country_name=country_name)
