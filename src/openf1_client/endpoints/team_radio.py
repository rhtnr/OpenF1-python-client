"""
Team Radio Endpoint.

Provides access to team radio communications.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import TeamRadio
from openf1_client.utils import FilterValue


class TeamRadioEndpoint(BaseEndpoint[TeamRadio]):
    """
    Endpoint for team radio communications.

    Contains metadata about radio messages between drivers and their
    teams, with URLs to audio recordings.

    Note: Only a selection of team radio communications are made
    available through this API.

    Example:
        >>> # Get all team radio for a session
        >>> radio = client.team_radio.list(session_key=9161)

        >>> # Get radio for a specific driver
        >>> driver_radio = client.team_radio.list(
        ...     session_key=9161,
        ...     driver_number=1,
        ... )

        >>> for msg in driver_radio:
        ...     print(f"Audio: {msg.recording_url}")
    """

    _endpoint = "team_radio"
    _model_class = TeamRadio

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[TeamRadio]:
        """
        Fetch team radio data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            **extra_filters: Additional filter parameters.

        Returns:
            List of TeamRadio instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            **extra_filters,
        )

    def get_driver_radio(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[TeamRadio]:
        """
        Get all team radio for a specific driver.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of TeamRadio instances for the driver.
        """
        return self.list(session_key=session_key, driver_number=driver_number)

    def get_radio_urls(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[str]:
        """
        Get all recording URLs for team radio.

        Args:
            session_key: The session identifier.
            driver_number: Optional driver number to filter by.

        Returns:
            List of recording URLs.
        """
        radio_data = self.list(session_key=session_key, driver_number=driver_number)
        return [r.recording_url for r in radio_data if r.recording_url]
