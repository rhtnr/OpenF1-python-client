"""
OpenF1 Python Client SDK.

A production-grade Python client for the OpenF1 Formula 1 API.
Provides easy access to real-time and historical F1 data including
telemetry, lap times, race control messages, and more.

Basic Usage:
    >>> from openf1_client import OpenF1Client
    >>> client = OpenF1Client()
    >>> laps = client.laps.list(session_key=9161, driver_number=63)
    >>> for lap in laps:
    ...     print(f"Lap {lap.lap_number}: {lap.lap_duration}s")

Authenticated Usage:
    >>> client = OpenF1Client(
    ...     username="user@example.com",
    ...     password="secret",
    ... )

For more information, see:
- API Documentation: https://openf1.org/
- Package Documentation: https://github.com/openf1-client/openf1-python
"""

from openf1_client.client import OpenF1Client
from openf1_client.config import ClientConfig
from openf1_client.errors import (
    OpenF1APIError,
    OpenF1AuthError,
    OpenF1ConfigError,
    OpenF1Error,
    OpenF1NotFoundError,
    OpenF1RateLimitError,
    OpenF1ServerError,
    OpenF1TimeoutError,
    OpenF1TransportError,
    OpenF1ValidationError,
)
from openf1_client.models import (
    CarData,
    Driver,
    Interval,
    Lap,
    Location,
    Meeting,
    Overtake,
    Pit,
    Position,
    RaceControl,
    Session,
    SessionResult,
    StartingGrid,
    Stint,
    TeamRadio,
    Weather,
)
from openf1_client.utils import FilterBuilder, setup_logging


__version__ = "1.0.0"
__all__ = [
    # Main client
    "OpenF1Client",
    "ClientConfig",
    # Errors
    "OpenF1Error",
    "OpenF1APIError",
    "OpenF1AuthError",
    "OpenF1ConfigError",
    "OpenF1NotFoundError",
    "OpenF1RateLimitError",
    "OpenF1ServerError",
    "OpenF1TimeoutError",
    "OpenF1TransportError",
    "OpenF1ValidationError",
    # Models
    "CarData",
    "Driver",
    "Interval",
    "Lap",
    "Location",
    "Meeting",
    "Overtake",
    "Pit",
    "Position",
    "RaceControl",
    "Session",
    "SessionResult",
    "StartingGrid",
    "Stint",
    "TeamRadio",
    "Weather",
    # Utilities
    "FilterBuilder",
    "setup_logging",
]
