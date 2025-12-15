"""Weather module for Open-Meteo API integration."""

from .client import OpenMeteoClient
from .constants import (
    EU_AQI_CATEGORIES,
    US_AQI_CATEGORIES,
    WEATHER_CODES,
    get_eu_aqi_category,
    get_us_aqi_category,
    get_weather_description,
)
from .conversions import (
    celsius_to_fahrenheit,
    degrees_to_compass,
    hpa_to_inhg,
    kmh_to_mph,
    mm_to_inches,
)
from .models import (
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

__all__ = [
    # Constants
    "WEATHER_CODES",
    "US_AQI_CATEGORIES",
    "EU_AQI_CATEGORIES",
    "get_weather_description",
    "get_us_aqi_category",
    "get_eu_aqi_category",
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
    # Conversions
    "celsius_to_fahrenheit",
    "kmh_to_mph",
    "hpa_to_inhg",
    "mm_to_inches",
    "degrees_to_compass",
    # Client
    "OpenMeteoClient",
]
