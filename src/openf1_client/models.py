"""
OpenF1 Data Models.

This module defines Pydantic models for the data structures returned
by the OpenF1 API. Models are designed to be permissive (allowing extra
fields) while providing strong typing for the most important fields.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class OpenF1BaseModel(BaseModel):
    """
    Base model for all OpenF1 data models.

    Configured to:
    - Allow extra fields (API may return fields not in our schema)
    - Use enum values directly
    - Populate by field name
    """

    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
        populate_by_name=True,
    )


# -----------------------------------------------------------------------------
# Meeting & Session Models
# -----------------------------------------------------------------------------


class Meeting(OpenF1BaseModel):
    """
    Represents a Formula 1 meeting (Grand Prix weekend or testing event).

    A meeting encompasses all sessions at a single venue, including
    practice, qualifying, sprint, and race sessions.
    """

    meeting_key: int = Field(..., description="Unique identifier for the meeting")
    meeting_name: str = Field(..., description="Name of the meeting (e.g., 'Monaco Grand Prix')")
    meeting_official_name: str | None = Field(None, description="Official FIA name")
    location: str | None = Field(None, description="City/location name")
    country_key: int | None = Field(None, description="Unique identifier for the country")
    country_code: str | None = Field(None, description="ISO 3166-1 alpha-3 country code")
    country_name: str | None = Field(None, description="Full country name")
    circuit_key: int | None = Field(None, description="Unique identifier for the circuit")
    circuit_short_name: str | None = Field(None, description="Short circuit name")
    date_start: datetime | str | None = Field(None, description="Meeting start date/time")
    gmt_offset: str | None = Field(None, description="GMT offset for local time")
    year: int | None = Field(None, description="Season year")


class Session(OpenF1BaseModel):
    """
    Represents a single session within a meeting.

    Sessions include practice (FP1, FP2, FP3), qualifying (Q),
    sprint shootout, sprint race, and the main race.
    """

    session_key: int = Field(..., description="Unique identifier for the session")
    session_name: str = Field(..., description="Name of the session (e.g., 'Race', 'Qualifying')")
    session_type: str | None = Field(None, description="Type of session")
    meeting_key: int | None = Field(None, description="Associated meeting identifier")
    date_start: datetime | str | None = Field(None, description="Session start time (UTC)")
    date_end: datetime | str | None = Field(None, description="Session end time (UTC)")
    gmt_offset: str | None = Field(None, description="GMT offset for local time")
    country_key: int | None = Field(None, description="Country identifier")
    country_code: str | None = Field(None, description="ISO country code")
    country_name: str | None = Field(None, description="Full country name")
    circuit_key: int | None = Field(None, description="Circuit identifier")
    circuit_short_name: str | None = Field(None, description="Short circuit name")
    year: int | None = Field(None, description="Season year")


# -----------------------------------------------------------------------------
# Driver Models
# -----------------------------------------------------------------------------


class Driver(OpenF1BaseModel):
    """
    Represents a driver's information for a specific session.

    Driver data can vary between sessions as drivers may switch
    teams or use different numbers during testing.
    """

    driver_number: int = Field(..., description="Driver's car number")
    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    broadcast_name: str | None = Field(None, description="Name shown on broadcasts")
    full_name: str | None = Field(None, description="Driver's full name")
    name_acronym: str | None = Field(None, description="Three-letter acronym (e.g., 'VER')")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    team_name: str | None = Field(None, description="Team name")
    team_colour: str | None = Field(None, description="Team color (hex without #)")
    headshot_url: str | None = Field(None, description="URL to driver headshot image")
    country_code: str | None = Field(None, description="Driver's nationality (ISO code)")


# -----------------------------------------------------------------------------
# Telemetry Models
# -----------------------------------------------------------------------------


class CarData(OpenF1BaseModel):
    """
    High-frequency car telemetry data (~3.7 Hz sampling rate).

    Contains real-time vehicle performance data including speed,
    RPM, throttle, brake, and gear information.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    speed: int | None = Field(None, description="Speed in km/h")
    rpm: int | None = Field(None, description="Engine RPM")
    n_gear: int | None = Field(None, description="Current gear (0-8, 0=neutral)")
    throttle: int | None = Field(None, description="Throttle percentage (0-100)")
    brake: int | None = Field(None, description="Brake percentage (0-100)")
    drs: int | None = Field(
        None,
        description=(
            "DRS status: 0-1=off, 8=eligible, 10-14=on/activated"
        ),
    )


class Location(OpenF1BaseModel):
    """
    Car position data on the circuit (~3.7 Hz sampling rate).

    Provides X, Y, Z coordinates representing the car's position
    on the track surface.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    x: int | None = Field(None, description="X coordinate (track-relative)")
    y: int | None = Field(None, description="Y coordinate (track-relative)")
    z: int | None = Field(None, description="Z coordinate (elevation)")


# -----------------------------------------------------------------------------
# Lap & Timing Models
# -----------------------------------------------------------------------------


class Lap(OpenF1BaseModel):
    """
    Detailed lap information including sector times and speeds.

    Contains comprehensive timing data for each completed lap,
    including intermediate speed trap measurements.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    lap_number: int | None = Field(None, description="Lap number in session")
    date_start: datetime | str | None = Field(None, description="Lap start time (UTC)")
    lap_duration: float | None = Field(None, description="Total lap time in seconds")
    duration_sector_1: float | None = Field(None, description="Sector 1 time in seconds")
    duration_sector_2: float | None = Field(None, description="Sector 2 time in seconds")
    duration_sector_3: float | None = Field(None, description="Sector 3 time in seconds")
    i1_speed: int | None = Field(None, description="Speed at intermediate 1 (km/h)")
    i2_speed: int | None = Field(None, description="Speed at intermediate 2 (km/h)")
    st_speed: int | None = Field(None, description="Speed trap speed (km/h)")
    is_pit_out_lap: bool | None = Field(None, description="Whether this is a pit out lap")
    segments_sector_1: list[int | None] | None = Field(None, description="Mini-sector status for S1")
    segments_sector_2: list[int | None] | None = Field(None, description="Mini-sector status for S2")
    segments_sector_3: list[int | None] | None = Field(None, description="Mini-sector status for S3")


class Interval(OpenF1BaseModel):
    """
    Gap/interval data between cars (~4-second update rate).

    Shows the time gap to the car ahead and to the race leader.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    gap_to_leader: float | str | None = Field(None, description="Gap to P1 in seconds")
    interval: float | str | None = Field(None, description="Gap to car ahead in seconds")


class Position(OpenF1BaseModel):
    """
    Driver position data throughout a session.

    Tracks position changes over time, useful for visualizing
    race progression.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    position: int | None = Field(None, description="Track position (1-20)")


# -----------------------------------------------------------------------------
# Pit & Stint Models
# -----------------------------------------------------------------------------


class Pit(OpenF1BaseModel):
    """
    Pit stop activity data.

    Records when drivers enter and exit the pit lane,
    along with pit stop duration.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    lap_number: int | None = Field(None, description="Lap number of pit entry")
    pit_duration: float | None = Field(None, description="Time in pit lane (seconds)")


class Stint(OpenF1BaseModel):
    """
    Continuous driving period (stint) data.

    A stint represents continuous track time between pit stops,
    including tyre compound and age information.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    stint_number: int | None = Field(None, description="Stint sequence number")
    lap_start: int | None = Field(None, description="First lap of stint")
    lap_end: int | None = Field(None, description="Last lap of stint")
    compound: str | None = Field(
        None,
        description="Tyre compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)",
    )
    tyre_age_at_start: int | None = Field(None, description="Tyre age at stint start (laps)")


# -----------------------------------------------------------------------------
# Race Control & Events
# -----------------------------------------------------------------------------


class RaceControl(OpenF1BaseModel):
    """
    Race control messages and events.

    Includes flags, safety car deployments, incidents,
    and other official race control communications.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Affected driver (if applicable)")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    lap_number: int | None = Field(None, description="Lap number")
    category: str | None = Field(None, description="Message category")
    flag: str | None = Field(
        None,
        description="Flag type (GREEN, YELLOW, RED, CHEQUERED, etc.)",
    )
    scope: str | None = Field(None, description="Flag scope (Track, Sector, Driver)")
    sector: int | None = Field(None, description="Affected sector (if applicable)")
    message: str | None = Field(None, description="Race control message text")


class Overtake(OpenF1BaseModel):
    """
    Overtaking event data (beta endpoint).

    Records passing maneuvers between drivers during race sessions.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Overtaking driver")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    lap_number: int | None = Field(None, description="Lap number")
    x: int | None = Field(None, description="X coordinate of overtake")
    y: int | None = Field(None, description="Y coordinate of overtake")


# -----------------------------------------------------------------------------
# Weather & Environment
# -----------------------------------------------------------------------------


class Weather(OpenF1BaseModel):
    """
    Weather and track condition data (~1-minute updates).

    Provides environmental data affecting car performance
    and strategy decisions.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    air_temperature: float | None = Field(None, description="Air temperature (Celsius)")
    track_temperature: float | None = Field(None, description="Track surface temperature (Celsius)")
    humidity: float | None = Field(None, description="Relative humidity (%)")
    pressure: float | None = Field(None, description="Atmospheric pressure (mbar)")
    wind_speed: float | None = Field(None, description="Wind speed (m/s)")
    wind_direction: int | None = Field(None, description="Wind direction (degrees, 0-359)")
    rainfall: bool | int | None = Field(None, description="Whether rain is falling")


# -----------------------------------------------------------------------------
# Team Radio
# -----------------------------------------------------------------------------


class TeamRadio(OpenF1BaseModel):
    """
    Team radio communications.

    Contains metadata about radio messages between drivers
    and their teams, with URLs to audio recordings.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    date: datetime | str | None = Field(None, description="Timestamp (UTC)")
    recording_url: str | None = Field(None, description="URL to audio recording")


# -----------------------------------------------------------------------------
# Session Results (Beta)
# -----------------------------------------------------------------------------


class SessionResult(OpenF1BaseModel):
    """
    Final session results (beta endpoint).

    Contains the final standings and classification for a session.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    position: int | None = Field(None, description="Final position")
    classified_position: str | int | None = Field(None, description="Classified position")
    status: str | None = Field(None, description="Finishing status")
    points: float | None = Field(None, description="Points awarded")


class StartingGrid(OpenF1BaseModel):
    """
    Starting grid positions (beta endpoint).

    Contains the grid positions at the start of a race or sprint.
    """

    session_key: int | None = Field(None, description="Associated session")
    meeting_key: int | None = Field(None, description="Associated meeting")
    driver_number: int | None = Field(None, description="Driver's car number")
    position: int | None = Field(None, description="Grid position")


# -----------------------------------------------------------------------------
# Type mapping for endpoint models
# -----------------------------------------------------------------------------

# Maps endpoint names to their corresponding model classes
ENDPOINT_MODELS: dict[str, type[OpenF1BaseModel]] = {
    "car_data": CarData,
    "drivers": Driver,
    "intervals": Interval,
    "laps": Lap,
    "location": Location,
    "meetings": Meeting,
    "overtakes": Overtake,
    "pit": Pit,
    "position": Position,
    "race_control": RaceControl,
    "sessions": Session,
    "session_result": SessionResult,
    "starting_grid": StartingGrid,
    "stints": Stint,
    "team_radio": TeamRadio,
    "weather": Weather,
}
