"""
OpenF1 API Endpoints.

This package contains endpoint classes for each OpenF1 API resource.
Each endpoint class provides a clean interface for interacting with
its corresponding API endpoint.
"""

from openf1_client.endpoints.base import BaseEndpoint
from openf1_client.endpoints.car_data import CarDataEndpoint
from openf1_client.endpoints.drivers import DriversEndpoint
from openf1_client.endpoints.intervals import IntervalsEndpoint
from openf1_client.endpoints.laps import LapsEndpoint
from openf1_client.endpoints.location import LocationEndpoint
from openf1_client.endpoints.meetings import MeetingsEndpoint
from openf1_client.endpoints.overtakes import OvertakesEndpoint
from openf1_client.endpoints.pit import PitEndpoint
from openf1_client.endpoints.position import PositionEndpoint
from openf1_client.endpoints.race_control import RaceControlEndpoint
from openf1_client.endpoints.sessions import SessionsEndpoint
from openf1_client.endpoints.session_result import SessionResultEndpoint
from openf1_client.endpoints.starting_grid import StartingGridEndpoint
from openf1_client.endpoints.stints import StintsEndpoint
from openf1_client.endpoints.team_radio import TeamRadioEndpoint
from openf1_client.endpoints.weather import WeatherEndpoint


__all__ = [
    "BaseEndpoint",
    "CarDataEndpoint",
    "DriversEndpoint",
    "IntervalsEndpoint",
    "LapsEndpoint",
    "LocationEndpoint",
    "MeetingsEndpoint",
    "OvertakesEndpoint",
    "PitEndpoint",
    "PositionEndpoint",
    "RaceControlEndpoint",
    "SessionsEndpoint",
    "SessionResultEndpoint",
    "StartingGridEndpoint",
    "StintsEndpoint",
    "TeamRadioEndpoint",
    "WeatherEndpoint",
]
