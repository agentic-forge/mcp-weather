"""Pytest configuration and fixtures."""

import pytest
import respx
from httpx import Response

from .fixtures import (
    AIR_QUALITY_POLLEN_RESPONSE,
    AIR_QUALITY_RESPONSE,
    CURRENT_WEATHER_IMPERIAL_RESPONSE,
    CURRENT_WEATHER_METRIC_RESPONSE,
    FORECAST_DAILY_RESPONSE,
    FORECAST_HOURLY_RESPONSE,
    GEOCODE_BERLIN_RESPONSE,
    GEOCODE_EMPTY_RESPONSE,
)


@pytest.fixture
def _mock_geocode_berlin(respx_mock: respx.MockRouter):
    """Mock successful geocoding response for Berlin."""
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params__contains={"name": "Berlin"},
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_geocode_empty(respx_mock: respx.MockRouter):
    """Mock empty geocoding response for non-existent location."""
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_EMPTY_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_current_weather_metric(respx_mock: respx.MockRouter):
    """Mock current weather response with metric units."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock weather
    respx_mock.get(
        "https://api.open-meteo.com/v1/forecast",
    ).mock(return_value=Response(200, json=CURRENT_WEATHER_METRIC_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_current_weather_imperial(respx_mock: respx.MockRouter):
    """Mock current weather response with imperial units."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock weather
    respx_mock.get(
        "https://api.open-meteo.com/v1/forecast",
    ).mock(return_value=Response(200, json=CURRENT_WEATHER_IMPERIAL_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_forecast_daily(respx_mock: respx.MockRouter):
    """Mock daily forecast response."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock forecast
    respx_mock.get(
        "https://api.open-meteo.com/v1/forecast",
    ).mock(return_value=Response(200, json=FORECAST_DAILY_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_forecast_hourly(respx_mock: respx.MockRouter):
    """Mock forecast with hourly data response."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock forecast
    respx_mock.get(
        "https://api.open-meteo.com/v1/forecast",
    ).mock(return_value=Response(200, json=FORECAST_HOURLY_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_air_quality(respx_mock: respx.MockRouter):
    """Mock air quality response without pollen."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock air quality
    respx_mock.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
    ).mock(return_value=Response(200, json=AIR_QUALITY_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_air_quality_pollen(respx_mock: respx.MockRouter):
    """Mock air quality response with pollen data."""
    # First mock geocoding
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
    # Then mock air quality
    respx_mock.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
    ).mock(return_value=Response(200, json=AIR_QUALITY_POLLEN_RESPONSE))
    return respx_mock


@pytest.fixture
def _mock_api_error(respx_mock: respx.MockRouter):
    """Mock API error response."""
    respx_mock.get(
        "https://geocoding-api.open-meteo.com/v1/search",
    ).mock(return_value=Response(500, text="Internal Server Error"))
    return respx_mock


@pytest.fixture
def _mock_coordinates_weather(respx_mock: respx.MockRouter):
    """Mock weather request using direct coordinates (no geocoding needed)."""
    respx_mock.get(
        "https://api.open-meteo.com/v1/forecast",
    ).mock(return_value=Response(200, json=CURRENT_WEATHER_METRIC_RESPONSE))
    return respx_mock
