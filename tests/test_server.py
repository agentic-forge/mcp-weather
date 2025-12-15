"""Tests for MCP server tools via the underlying client.

The server tools are thin wrappers around the OpenMeteoClient.
These tests verify the integration by testing the same flow
the server tools would use.
"""

import pytest
import respx
from httpx import Response

from forge_mcp_weather.server import client, mcp

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


class TestGeocodeTool:
    """Tests for the geocode tool functionality."""

    @respx.mock
    async def test_geocode_tool(self):
        """Test the geocode returns locations."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))

        # Use the client directly (same as what the tool uses)
        locations = await client.geocode("Berlin")

        assert len(locations) == 2
        assert locations[0].name == "Berlin"
        assert locations[0].country == "Germany"

    @respx.mock
    async def test_geocode_tool_with_country_filter(self):
        """Test the geocode with country filter."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))

        locations = await client.geocode("Berlin", country="US")

        # Should only return US locations
        assert all(loc.country == "United States" for loc in locations)

    @respx.mock
    async def test_geocode_tool_empty_results(self):
        """Test the geocode with no results."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_EMPTY_RESPONSE))

        locations = await client.geocode("xyznonexistent")

        assert locations == []


class TestGetCurrentWeatherTool:
    """Tests for the get_current_weather tool functionality."""

    @respx.mock
    async def test_current_weather_by_city(self):
        """Test getting current weather by city."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=Response(200, json=CURRENT_WEATHER_METRIC_RESPONSE))

        weather = await client.get_current_weather(city="Berlin")

        assert "Berlin" in weather.location
        assert weather.temperature == pytest.approx(5.9)
        assert weather.units.temperature == "°C"

    @respx.mock
    async def test_current_weather_by_coordinates(self):
        """Test getting current weather by coordinates."""
        respx.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=Response(200, json=CURRENT_WEATHER_METRIC_RESPONSE))

        weather = await client.get_current_weather(latitude=52.52, longitude=13.41)

        assert weather.coordinates == (52.52, 13.41)

    @respx.mock
    async def test_current_weather_imperial_units(self):
        """Test getting current weather with imperial units."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=Response(200, json=CURRENT_WEATHER_IMPERIAL_RESPONSE))

        weather = await client.get_current_weather(city="Berlin", units="imperial")

        assert weather.units.temperature == "°F"
        assert weather.units.wind_speed == "mph"


class TestGetForecastTool:
    """Tests for the get_forecast tool functionality."""

    @respx.mock
    async def test_forecast_daily(self):
        """Test getting daily forecast."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=Response(200, json=FORECAST_DAILY_RESPONSE))

        forecast = await client.get_forecast(city="Berlin", days=3)

        assert "Berlin" in forecast.location
        assert len(forecast.daily) == 3
        assert forecast.hourly is None

    @respx.mock
    async def test_forecast_with_hourly(self):
        """Test getting forecast with hourly breakdown."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=Response(200, json=FORECAST_HOURLY_RESPONSE))

        forecast = await client.get_forecast(city="Berlin", days=1, hourly=True)

        assert forecast.hourly is not None
        assert len(forecast.hourly) > 0


class TestGetAirQualityTool:
    """Tests for the get_air_quality tool functionality."""

    @respx.mock
    async def test_air_quality_basic(self):
        """Test getting air quality data."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
        ).mock(return_value=Response(200, json=AIR_QUALITY_RESPONSE))

        aq = await client.get_air_quality(city="Berlin")

        assert "Berlin" in aq.location
        assert aq.us_aqi.value == 57
        assert aq.pollen is None

    @respx.mock
    async def test_air_quality_with_pollen(self):
        """Test getting air quality with pollen data."""
        respx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        ).mock(return_value=Response(200, json=GEOCODE_BERLIN_RESPONSE))
        respx.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
        ).mock(return_value=Response(200, json=AIR_QUALITY_POLLEN_RESPONSE))

        aq = await client.get_air_quality(city="Berlin", include_pollen=True)

        assert aq.pollen is not None


class TestServerModule:
    """Tests for the server module itself."""

    def test_mcp_server_exists(self):
        """Test that the MCP server is properly created."""
        assert mcp is not None
        assert mcp.name == "Weather Server"

    def test_tools_are_registered(self):
        """Test that all tools are registered with the MCP server."""
        # Get registered tools
        tools = list(mcp._tool_manager._tools.keys())

        assert "geocode" in tools
        assert "get_current_weather" in tools
        assert "get_forecast" in tools
        assert "get_air_quality" in tools
