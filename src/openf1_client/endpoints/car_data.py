"""
Car Data Endpoint.

Provides access to high-frequency car telemetry data including
speed, RPM, throttle, brake, and DRS status.
"""

from __future__ import annotations

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.models import CarData
from openf1_client.utils import FilterValue


class CarDataEndpoint(BaseEndpoint[CarData]):
    """
    Endpoint for car telemetry data.

    Car data is sampled at approximately 3.7 Hz and includes:
    - Speed (km/h)
    - Engine RPM
    - Gear position
    - Throttle percentage (0-100)
    - Brake percentage (0-100)
    - DRS status

    Example:
        >>> # Get telemetry for a specific driver at high speed
        >>> car_data = client.car_data.list(
        ...     session_key=9159,
        ...     driver_number=55,
        ...     speed={">=": 315},
        ... )

        >>> # Get telemetry during a specific time window
        >>> car_data = client.car_data.list(
        ...     session_key=9161,
        ...     driver_number=81,
        ...     date={">": "2023-09-16T13:03:35.200", "<": "2023-09-16T13:03:35.800"},
        ... )
    """

    _endpoint = "car_data"
    _model_class = CarData

    def list(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
        driver_number: int | None = None,
        date: FilterValue | None = None,
        speed: FilterValue | None = None,
        rpm: FilterValue | None = None,
        n_gear: FilterValue | None = None,
        throttle: FilterValue | None = None,
        brake: FilterValue | None = None,
        drs: FilterValue | None = None,
        **extra_filters: FilterValue | None,
    ) -> list[CarData]:
        """
        Fetch car telemetry data.

        Args:
            session_key: Filter by session (use "latest" for current session).
            meeting_key: Filter by meeting (use "latest" for current meeting).
            driver_number: Filter by driver number.
            date: Filter by timestamp (supports comparison operators).
            speed: Filter by speed in km/h (supports comparison operators).
            rpm: Filter by engine RPM (supports comparison operators).
            n_gear: Filter by gear (0-8).
            throttle: Filter by throttle percentage (0-100).
            brake: Filter by brake percentage (0-100).
            drs: Filter by DRS status.
            **extra_filters: Additional filter parameters.

        Returns:
            List of CarData instances.
        """
        return super().list(
            session_key=session_key,
            meeting_key=meeting_key,
            driver_number=driver_number,
            date=date,
            speed=speed,
            rpm=rpm,
            n_gear=n_gear,
            throttle=throttle,
            brake=brake,
            drs=drs,
            **extra_filters,
        )

    def get_high_speed_moments(
        self,
        session_key: int | str,
        driver_number: int,
        min_speed: int = 300,
    ) -> list[CarData]:
        """
        Get telemetry data for high-speed moments.

        Convenience method to find telemetry data when a driver
        exceeds a certain speed threshold.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.
            min_speed: Minimum speed threshold in km/h (default: 300).

        Returns:
            List of CarData instances exceeding the speed threshold.
        """
        return self.list(
            session_key=session_key,
            driver_number=driver_number,
            speed={">=": min_speed},
        )

    def get_drs_activations(
        self,
        session_key: int | str,
        driver_number: int,
    ) -> list[CarData]:
        """
        Get telemetry data where DRS is activated.

        DRS status codes 10-14 indicate DRS is active.

        Args:
            session_key: The session identifier.
            driver_number: The driver's car number.

        Returns:
            List of CarData instances with DRS active.
        """
        return self.list(
            session_key=session_key,
            driver_number=driver_number,
            drs={">=": 10},
        )
