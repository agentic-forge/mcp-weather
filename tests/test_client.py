"""Tests for the OpenMeteoClient."""

import pytest
import respx
from httpx import Response

from forge_mcp_weather.weather.client import (
    APIError,
    LocationNotFoundError,
    OpenMeteoClient,
    WeatherError,
)

from .fixtures import AIR_QUALITY_RESPONSE


class TestGeocode:
    """Tests for the geocode method."""

    @respx.mock
    async def test_geocode_returns_locations(self, _mock_geocode_berlin):
        """Test that geocode returns a list of locations."""
        client = OpenMeteoClient()
        locations = await client.geocode("Berlin")

        assert len(locations) == 2
        assert locations[0].name == "Berlin"
        assert locations[0].country == "Germany"
        assert locations[0].country_code == "DE"
        assert locations[0].latitude == pytest.approx(52.52437)
        assert locations[0].longitude == pytest.approx(13.41053)
        assert locations[0].timezone == "Europe/Berlin"
        assert locations[0].population == 3426354

    @respx.mock
    async def test_geocode_sorts_by_population(self, _mock_geocode_berlin):
        """Test that locations are sorted by population (highest first)."""
        client = OpenMeteoClient()
        locations = await client.geocode("Berlin")

        # Berlin, Germany should be first (higher population)
        assert locations[0].country == "Germany"
        assert locations[0].population > locations[1].population

    @respx.mock
    async def test_geocode_empty_returns_empty_list(self, _mock_geocode_empty):
        """Test that geocode returns empty list for non-existent location."""
        client = OpenMeteoClient()
        locations = await client.geocode("xyznonexistent12345")

        assert locations == []

    @respx.mock
    async def test_geocode_filters_by_country(self, _mock_geocode_berlin):
        """Test that geocode filters by country when specified."""
        client = OpenMeteoClient()

        # Filter by US
        locations = await client.geocode("Berlin", country="US")
        assert all(loc.country_code == "US" for loc in locations)

        # The fixture has both DE and US results
        client2 = OpenMeteoClient()
        all_locations = await client2.geocode("Berlin")
        assert len(all_locations) > len(locations)

    @respx.mock
    async def test_geocode_api_error(self, _mock_api_error):
        """Test that API errors are raised as APIError."""
        client = OpenMeteoClient()

        with pytest.raises(APIError, match="API request failed"):
            await client.geocode("Berlin")


class TestResolveLocation:
    """Tests for location resolution."""

    @respx.mock
    async def test_resolve_with_coordinates(self, _mock_geocode_berlin):
        """Test resolving location with direct coordinates."""
        client = OpenMeteoClient()
        lat, lon, name = await client.resolve_location(latitude=52.52, longitude=13.41)

        assert lat == 52.52
        assert lon == 13.41
        assert "52.5200" in name
        assert "13.4100" in name

    @respx.mock
    async def test_resolve_with_city(self, _mock_geocode_berlin):
        """Test resolving location with city name."""
        client = OpenMeteoClient()
        lat, lon, name = await client.resolve_location(city="Berlin")

        assert lat == pytest.approx(52.52437)
        assert lon == pytest.approx(13.41053)
        assert "Berlin" in name
        assert "Germany" in name

    @respx.mock
    async def test_resolve_city_not_found(self, _mock_geocode_empty):
        """Test that LocationNotFoundError is raised for unknown city."""
        client = OpenMeteoClient()

        with pytest.raises(LocationNotFoundError, match="No location found"):
            await client.resolve_location(city="xyznonexistent12345")

    async def test_resolve_no_location_provided(self):
        """Test that WeatherError is raised when no location is provided."""
        client = OpenMeteoClient()

        with pytest.raises(WeatherError, match="Provide either city name"):
            await client.resolve_location()


class TestGetCurrentWeather:
    """Tests for the get_current_weather method."""

    @respx.mock
    async def test_current_weather_by_city(self, _mock_current_weather_metric):
        """Test getting current weather by city name."""
        client = OpenMeteoClient()
        weather = await client.get_current_weather(city="Berlin")

        assert "Berlin" in weather.location
        assert weather.temperature == pytest.approx(5.9)
        assert weather.feels_like == pytest.approx(2.7)
        assert weather.humidity == 82
        assert weather.weather_code == 2
        assert weather.weather_description == "Partly cloudy"
        assert weather.wind_speed == pytest.approx(11.0)
        assert weather.wind_direction == 221
        assert weather.wind_direction_compass == "SW"
        assert weather.pressure == pytest.approx(1025.5)
        assert weather.units.temperature == "°C"
        assert weather.units.wind_speed == "km/h"

    @respx.mock
    async def test_current_weather_by_coordinates(self, _mock_coordinates_weather):
        """Test getting current weather by coordinates."""
        client = OpenMeteoClient()
        weather = await client.get_current_weather(latitude=52.52, longitude=13.41)

        assert weather.coordinates == (52.52, 13.41)
        assert weather.temperature == pytest.approx(5.9)

    @respx.mock
    async def test_current_weather_imperial(self, _mock_current_weather_imperial):
        """Test getting current weather with imperial units."""
        client = OpenMeteoClient()
        weather = await client.get_current_weather(city="Berlin", units="imperial")

        assert weather.temperature == pytest.approx(42.6)
        assert weather.feels_like == pytest.approx(36.9)
        assert weather.units.temperature == "°F"
        assert weather.units.wind_speed == "mph"


class TestGetForecast:
    """Tests for the get_forecast method."""

    @respx.mock
    async def test_forecast_daily(self, _mock_forecast_daily):
        """Test getting daily forecast."""
        client = OpenMeteoClient()
        forecast = await client.get_forecast(city="Berlin", days=3)

        assert "Berlin" in forecast.location
        assert len(forecast.daily) == 3
        assert forecast.hourly is None

        # Check first day
        day1 = forecast.daily[0]
        assert day1.date == "2025-12-14"
        assert day1.temperature_max == pytest.approx(7.2)
        assert day1.temperature_min == pytest.approx(4.6)
        assert day1.weather_code == 3
        assert day1.weather_description == "Overcast"
        assert day1.sunrise == "08:10"
        assert day1.sunset == "15:51"

    @respx.mock
    async def test_forecast_with_hourly(self, _mock_forecast_hourly):
        """Test getting forecast with hourly breakdown."""
        client = OpenMeteoClient()
        forecast = await client.get_forecast(city="Berlin", days=1, hourly=True)

        assert forecast.hourly is not None
        assert len(forecast.hourly) == 3

        hour1 = forecast.hourly[0]
        assert hour1.time == "2025-12-14T00:00"
        assert hour1.temperature == pytest.approx(5.5)
        assert hour1.weather_code == 3


class TestGetAirQuality:
    """Tests for the get_air_quality method."""

    @respx.mock
    async def test_air_quality_basic(self, _mock_air_quality):
        """Test getting air quality data."""
        client = OpenMeteoClient()
        aq = await client.get_air_quality(city="Berlin")

        assert "Berlin" in aq.location
        assert aq.us_aqi.value == 57
        assert aq.us_aqi.category == "Moderate"
        assert aq.european_aqi.value == 31
        assert aq.european_aqi.category == "Fair"

        # Pollutants
        assert aq.pollutants.pm2_5 == pytest.approx(13.6)
        assert aq.pollutants.pm10 == pytest.approx(15.4)
        assert aq.pollutants.ozone == pytest.approx(35.0)

        # No pollen data
        assert aq.pollen is None

    @respx.mock
    async def test_air_quality_with_pollen(self, _mock_air_quality_pollen):
        """Test getting air quality data with pollen."""
        client = OpenMeteoClient()
        aq = await client.get_air_quality(city="Berlin", include_pollen=True)

        assert aq.pollen is not None
        assert aq.pollen.alder == pytest.approx(0.0)
        assert aq.pollen.birch == pytest.approx(0.0)
        assert aq.pollen.grass == pytest.approx(0.0)

    @respx.mock
    async def test_air_quality_by_coordinates(self, respx_mock):
        """Test getting air quality by coordinates."""
        respx_mock.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
        ).mock(return_value=Response(200, json=AIR_QUALITY_RESPONSE))

        client = OpenMeteoClient()
        aq = await client.get_air_quality(latitude=52.52, longitude=13.41)

        assert aq.coordinates == (52.52, 13.41)
        assert aq.us_aqi.value == 57
