"""Weather MCP Server using FastMCP and Open-Meteo API."""

from .server import main, mcp
from .weather.client import APIError, LocationNotFoundError, OpenMeteoClient, WeatherError
from .weather.models import (
    AirQuality,
    AirQualityIndex,
    CurrentWeather,
    DailyForecast,
    Forecast,
    HourlyForecast,
    Location,
    PollenLevels,
    Pollutants,
    WeatherUnits,
)

__version__ = "0.1.0"

__all__ = [
    # Server
    "mcp",
    "main",
    # Client
    "OpenMeteoClient",
    # Exceptions
    "WeatherError",
    "LocationNotFoundError",
    "APIError",
    # Models
    "Location",
    "WeatherUnits",
    "CurrentWeather",
    "DailyForecast",
    "HourlyForecast",
    "Forecast",
    "AirQualityIndex",
    "Pollutants",
    "PollenLevels",
    "AirQuality",
]
