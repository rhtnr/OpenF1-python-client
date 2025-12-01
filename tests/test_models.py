"""Tests for the Pydantic models."""

import pytest
from pydantic import ValidationError

from openf1_client.models import (
    CarData,
    Driver,
    Interval,
    Lap,
    Location,
    Meeting,
    Pit,
    Position,
    RaceControl,
    Session,
    Stint,
    TeamRadio,
    Weather,
)


class TestCarData:
    """Tests for CarData model."""

    def test_valid_car_data(self) -> None:
        """Test creating valid CarData."""
        data = CarData(
            session_key=9161,
            driver_number=1,
            speed=315,
            rpm=12000,
            n_gear=7,
            throttle=100,
            brake=0,
            drs=10,
        )

        assert data.speed == 315
        assert data.rpm == 12000
        assert data.n_gear == 7

    def test_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed."""
        data = CarData.model_validate({
            "session_key": 9161,
            "unknown_field": "value",
        })

        assert data.session_key == 9161

    def test_optional_fields(self) -> None:
        """Test optional fields default to None."""
        data = CarData()

        assert data.session_key is None
        assert data.speed is None
        assert data.drs is None


class TestDriver:
    """Tests for Driver model."""

    def test_valid_driver(self) -> None:
        """Test creating valid Driver."""
        data = Driver(
            driver_number=1,
            full_name="Max Verstappen",
            name_acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        )

        assert data.driver_number == 1
        assert data.full_name == "Max Verstappen"
        assert data.name_acronym == "VER"

    def test_from_api_response(self) -> None:
        """Test creating Driver from API response."""
        api_data = {
            "driver_number": 44,
            "broadcast_name": "L HAMILTON",
            "full_name": "Lewis Hamilton",
            "name_acronym": "HAM",
            "team_name": "Mercedes",
            "team_colour": "27F4D2",
            "first_name": "Lewis",
            "last_name": "Hamilton",
            "country_code": "GBR",
        }

        driver = Driver.model_validate(api_data)

        assert driver.driver_number == 44
        assert driver.broadcast_name == "L HAMILTON"
        assert driver.country_code == "GBR"


class TestLap:
    """Tests for Lap model."""

    def test_valid_lap(self) -> None:
        """Test creating valid Lap."""
        data = Lap(
            session_key=9161,
            driver_number=63,
            lap_number=1,
            lap_duration=92.456,
            duration_sector_1=28.123,
            duration_sector_2=35.456,
            duration_sector_3=28.877,
        )

        assert data.lap_number == 1
        assert data.lap_duration == 92.456
        assert data.duration_sector_1 == 28.123

    def test_segments(self) -> None:
        """Test lap with segment data."""
        data = Lap(
            lap_number=1,
            segments_sector_1=[2049, 2049, 2048],
            segments_sector_2=[2049, 2051, 2049],
            segments_sector_3=[2048, 2048, 2049],
        )

        assert data.segments_sector_1 == [2049, 2049, 2048]
        assert 2051 in data.segments_sector_2  # type: ignore


class TestInterval:
    """Tests for Interval model."""

    def test_valid_interval(self) -> None:
        """Test creating valid Interval."""
        data = Interval(
            session_key=9161,
            driver_number=1,
            gap_to_leader=0.0,
            interval=0.0,
        )

        assert data.gap_to_leader == 0.0
        assert data.interval == 0.0

    def test_string_gap(self) -> None:
        """Test interval with string gap (e.g., for lapped cars)."""
        data = Interval(
            driver_number=20,
            gap_to_leader="+1 LAP",
            interval=5.234,
        )

        assert data.gap_to_leader == "+1 LAP"


class TestSession:
    """Tests for Session model."""

    def test_valid_session(self) -> None:
        """Test creating valid Session."""
        data = Session(
            session_key=9161,
            session_name="Race",
            meeting_key=1219,
            country_name="Singapore",
            circuit_short_name="Marina Bay",
        )

        assert data.session_key == 9161
        assert data.session_name == "Race"


class TestMeeting:
    """Tests for Meeting model."""

    def test_valid_meeting(self) -> None:
        """Test creating valid Meeting."""
        data = Meeting(
            meeting_key=1219,
            meeting_name="Singapore Grand Prix",
            location="Singapore",
            country_name="Singapore",
            year=2023,
        )

        assert data.meeting_key == 1219
        assert data.meeting_name == "Singapore Grand Prix"


class TestWeather:
    """Tests for Weather model."""

    def test_valid_weather(self) -> None:
        """Test creating valid Weather."""
        data = Weather(
            session_key=9161,
            air_temperature=28.5,
            track_temperature=35.2,
            humidity=78.0,
            pressure=1012.5,
            wind_speed=2.5,
            wind_direction=180,
            rainfall=False,
        )

        assert data.air_temperature == 28.5
        assert data.track_temperature == 35.2
        assert data.rainfall is False


class TestStint:
    """Tests for Stint model."""

    def test_valid_stint(self) -> None:
        """Test creating valid Stint."""
        data = Stint(
            session_key=9161,
            driver_number=1,
            stint_number=1,
            lap_start=1,
            lap_end=25,
            compound="MEDIUM",
            tyre_age_at_start=0,
        )

        assert data.stint_number == 1
        assert data.compound == "MEDIUM"
        assert data.tyre_age_at_start == 0


class TestPit:
    """Tests for Pit model."""

    def test_valid_pit(self) -> None:
        """Test creating valid Pit."""
        data = Pit(
            session_key=9161,
            driver_number=1,
            lap_number=25,
            pit_duration=23.456,
        )

        assert data.lap_number == 25
        assert data.pit_duration == 23.456


class TestRaceControl:
    """Tests for RaceControl model."""

    def test_valid_race_control(self) -> None:
        """Test creating valid RaceControl."""
        data = RaceControl(
            session_key=9161,
            category="Flag",
            flag="YELLOW",
            scope="Sector",
            sector=1,
            message="Yellow flag in sector 1",
        )

        assert data.flag == "YELLOW"
        assert data.scope == "Sector"
        assert data.sector == 1


class TestPosition:
    """Tests for Position model."""

    def test_valid_position(self) -> None:
        """Test creating valid Position."""
        data = Position(
            session_key=9161,
            driver_number=1,
            position=1,
        )

        assert data.position == 1


class TestLocation:
    """Tests for Location model."""

    def test_valid_location(self) -> None:
        """Test creating valid Location."""
        data = Location(
            session_key=9161,
            driver_number=1,
            x=1234,
            y=5678,
            z=100,
        )

        assert data.x == 1234
        assert data.y == 5678
        assert data.z == 100


class TestTeamRadio:
    """Tests for TeamRadio model."""

    def test_valid_team_radio(self) -> None:
        """Test creating valid TeamRadio."""
        data = TeamRadio(
            session_key=9161,
            driver_number=1,
            recording_url="https://example.com/radio.mp3",
        )

        assert data.recording_url == "https://example.com/radio.mp3"
