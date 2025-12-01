"""
Weather Endpoint.

Provides access to weather and track condition data.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import Weather
from openf1_client.utils import FilterValue


class WeatherEndpoint(BaseEndpoint[Weather]):
    """
    Endpoint for weather and track condition data.

    Weather data is updated approximately every minute and includes
    air and track temperature, humidity, pressure, and wind conditions.

    Example:
        >>> # Get weather for a session
        >>> weather = client.weather.list(session_key=9161)

        >>> # Get current conditions
        >>> current = client.weather.first(session_key="latest")
        >>> print(f"Air: {current.air_temperature}°C, "
        ...       f"Track: {current.track_temperature}°C")

        >>> # Get hot track conditions
        >>> hot_track = client.weather.list(
        ...     session_key=9161,
        ...     track_temperature={">=": 45.0},
        ... )
    """

    _endpoint = "weather"
    _model_class = Weather

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        date: FilterValue | None = None,
        air_temperature: FilterValue | None = None,
        track_temperature: FilterValue | None = None,
        humidity: FilterValue | None = None,
        pressure: FilterValue | None = None,
        wind_speed: FilterValue | None = None,
        wind_direction: FilterValue | None = None,
        rainfall: bool | int | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[Weather]:
        """
        Fetch weather data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            date: Filter by timestamp (supports comparison operators).
            air_temperature: Filter by air temp in °C (supports comparisons).
            track_temperature: Filter by track temp in °C (supports comparisons).
            humidity: Filter by humidity % (supports comparison operators).
            pressure: Filter by pressure in mbar (supports comparisons).
            wind_speed: Filter by wind speed in m/s (supports comparisons).
            wind_direction: Filter by wind direction in degrees.
            rainfall: Filter by rainfall status (True/False).
            **extra_filters: Additional filter parameters.

        Returns:
            List of Weather instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            date=date,
            air_temperature=air_temperature,
            track_temperature=track_temperature,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            rainfall=rainfall,
            **extra_filters,
        )

    def get_latest(self, session_key: int | str) -> Weather | None:
        """
        Get the most recent weather reading for a session.

        Args:
            session_key: The session identifier.

        Returns:
            The most recent Weather instance, or None if no data.
        """
        weather_data = self.list(session_key=session_key)
        if not weather_data:
            return None
        # Data is typically returned in chronological order
        return weather_data[-1] if weather_data else None

    def get_rain_periods(self, session_key: int | str) -> list[Weather]:
        """
        Get weather readings during rainfall.

        Args:
            session_key: The session identifier.

        Returns:
            List of Weather instances with rainfall.
        """
        return self.list(session_key=session_key, rainfall=True)

    def get_temperature_extremes(
        self,
        session_key: int | str,
    ) -> dict[str, Weather | None]:
        """
        Get temperature extremes for a session.

        Args:
            session_key: The session identifier.

        Returns:
            Dictionary with 'hottest' and 'coldest' Weather instances.
        """
        weather_data = self.list(session_key=session_key)
        if not weather_data:
            return {"hottest": None, "coldest": None}

        with_track_temp = [w for w in weather_data if w.track_temperature is not None]
        if not with_track_temp:
            return {"hottest": None, "coldest": None}

        hottest = max(with_track_temp, key=lambda w: w.track_temperature or 0)
        coldest = min(with_track_temp, key=lambda w: w.track_temperature or float("inf"))

        return {"hottest": hottest, "coldest": coldest}
