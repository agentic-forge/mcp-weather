"""Tests for utility functions (conversions and constants)."""

import pytest

from forge_mcp_weather.weather.constants import (
    get_eu_aqi_category,
    get_us_aqi_category,
    get_weather_description,
)
from forge_mcp_weather.weather.conversions import (
    celsius_to_fahrenheit,
    degrees_to_compass,
    fahrenheit_to_celsius,
    hpa_to_inhg,
    inches_to_mm,
    inhg_to_hpa,
    kmh_to_mph,
    mm_to_inches,
    mph_to_kmh,
)


class TestTemperatureConversions:
    """Tests for temperature conversion functions."""

    def test_celsius_to_fahrenheit(self):
        assert celsius_to_fahrenheit(0) == pytest.approx(32)
        assert celsius_to_fahrenheit(100) == pytest.approx(212)
        assert celsius_to_fahrenheit(-40) == pytest.approx(-40)
        assert celsius_to_fahrenheit(20) == pytest.approx(68)

    def test_fahrenheit_to_celsius(self):
        assert fahrenheit_to_celsius(32) == pytest.approx(0)
        assert fahrenheit_to_celsius(212) == pytest.approx(100)
        assert fahrenheit_to_celsius(-40) == pytest.approx(-40)
        assert fahrenheit_to_celsius(68) == pytest.approx(20)

    def test_temperature_roundtrip(self):
        """Test that converting back and forth returns original value."""
        original = 25.5
        converted = celsius_to_fahrenheit(original)
        back = fahrenheit_to_celsius(converted)
        assert back == pytest.approx(original)


class TestWindSpeedConversions:
    """Tests for wind speed conversion functions."""

    def test_kmh_to_mph(self):
        assert kmh_to_mph(100) == pytest.approx(62.1371)
        assert kmh_to_mph(0) == pytest.approx(0)

    def test_mph_to_kmh(self):
        assert mph_to_kmh(62.1371) == pytest.approx(100, rel=0.01)
        assert mph_to_kmh(0) == pytest.approx(0)

    def test_wind_speed_roundtrip(self):
        original = 50.0
        converted = kmh_to_mph(original)
        back = mph_to_kmh(converted)
        assert back == pytest.approx(original)


class TestPressureConversions:
    """Tests for pressure conversion functions."""

    def test_hpa_to_inhg(self):
        # Standard sea level pressure
        assert hpa_to_inhg(1013.25) == pytest.approx(29.92, rel=0.01)

    def test_inhg_to_hpa(self):
        assert inhg_to_hpa(29.92) == pytest.approx(1013.25, rel=0.01)

    def test_pressure_roundtrip(self):
        original = 1020.0
        converted = hpa_to_inhg(original)
        back = inhg_to_hpa(converted)
        assert back == pytest.approx(original)


class TestPrecipitationConversions:
    """Tests for precipitation conversion functions."""

    def test_mm_to_inches(self):
        assert mm_to_inches(25.4) == pytest.approx(1.0, rel=0.01)
        assert mm_to_inches(0) == pytest.approx(0)

    def test_inches_to_mm(self):
        assert inches_to_mm(1.0) == pytest.approx(25.4, rel=0.01)
        assert inches_to_mm(0) == pytest.approx(0)

    def test_precipitation_roundtrip(self):
        original = 10.0
        converted = mm_to_inches(original)
        back = inches_to_mm(converted)
        assert back == pytest.approx(original)


class TestDegreesToCompass:
    """Tests for wind direction compass conversion."""

    def test_cardinal_directions(self):
        assert degrees_to_compass(0) == "N"
        assert degrees_to_compass(90) == "E"
        assert degrees_to_compass(180) == "S"
        assert degrees_to_compass(270) == "W"
        assert degrees_to_compass(360) == "N"

    def test_intercardinal_directions(self):
        assert degrees_to_compass(45) == "NE"
        assert degrees_to_compass(135) == "SE"
        assert degrees_to_compass(225) == "SW"
        assert degrees_to_compass(315) == "NW"

    def test_16_point_directions(self):
        assert degrees_to_compass(22) == "NNE"
        assert degrees_to_compass(67) == "ENE"
        assert degrees_to_compass(112) == "ESE"
        assert degrees_to_compass(157) == "SSE"
        assert degrees_to_compass(202) == "SSW"
        assert degrees_to_compass(247) == "WSW"
        assert degrees_to_compass(292) == "WNW"
        assert degrees_to_compass(337) == "NNW"

    def test_real_api_value(self):
        # The actual API returned 221 degrees for Berlin
        assert degrees_to_compass(221) == "SW"

    def test_handles_values_over_360(self):
        assert degrees_to_compass(450) == "E"  # 450 - 360 = 90
        assert degrees_to_compass(720) == "N"  # 720 - 720 = 0


class TestWeatherDescriptions:
    """Tests for weather code descriptions."""

    def test_clear_conditions(self):
        assert get_weather_description(0) == "Clear sky"
        assert get_weather_description(1) == "Mainly clear"
        assert get_weather_description(2) == "Partly cloudy"
        assert get_weather_description(3) == "Overcast"

    def test_fog_conditions(self):
        assert get_weather_description(45) == "Fog"
        assert get_weather_description(48) == "Depositing rime fog"

    def test_rain_conditions(self):
        assert get_weather_description(61) == "Slight rain"
        assert get_weather_description(63) == "Moderate rain"
        assert get_weather_description(65) == "Heavy rain"

    def test_snow_conditions(self):
        assert get_weather_description(71) == "Slight snow fall"
        assert get_weather_description(73) == "Moderate snow fall"
        assert get_weather_description(75) == "Heavy snow fall"

    def test_thunderstorm_conditions(self):
        assert get_weather_description(95) == "Thunderstorm"
        assert get_weather_description(96) == "Thunderstorm with slight hail"
        assert get_weather_description(99) == "Thunderstorm with heavy hail"

    def test_unknown_code(self):
        result = get_weather_description(999)
        assert "Unknown" in result
        assert "999" in result


class TestUSAQICategories:
    """Tests for US EPA AQI categories."""

    def test_good_category(self):
        assert get_us_aqi_category(0) == "Good"
        assert get_us_aqi_category(25) == "Good"
        assert get_us_aqi_category(50) == "Good"

    def test_moderate_category(self):
        assert get_us_aqi_category(51) == "Moderate"
        assert get_us_aqi_category(75) == "Moderate"
        assert get_us_aqi_category(100) == "Moderate"

    def test_unhealthy_sensitive(self):
        assert get_us_aqi_category(101) == "Unhealthy for Sensitive Groups"
        assert get_us_aqi_category(150) == "Unhealthy for Sensitive Groups"

    def test_unhealthy(self):
        assert get_us_aqi_category(151) == "Unhealthy"
        assert get_us_aqi_category(200) == "Unhealthy"

    def test_very_unhealthy(self):
        assert get_us_aqi_category(201) == "Very Unhealthy"
        assert get_us_aqi_category(300) == "Very Unhealthy"

    def test_hazardous(self):
        assert get_us_aqi_category(301) == "Hazardous"
        assert get_us_aqi_category(500) == "Hazardous"

    def test_real_api_value(self):
        # The actual API returned 57 for Berlin
        assert get_us_aqi_category(57) == "Moderate"


class TestEUAQICategories:
    """Tests for European AQI categories."""

    def test_good_category(self):
        assert get_eu_aqi_category(0) == "Good"
        assert get_eu_aqi_category(20) == "Good"

    def test_fair_category(self):
        assert get_eu_aqi_category(21) == "Fair"
        assert get_eu_aqi_category(40) == "Fair"

    def test_moderate_category(self):
        assert get_eu_aqi_category(41) == "Moderate"
        assert get_eu_aqi_category(60) == "Moderate"

    def test_poor_category(self):
        assert get_eu_aqi_category(61) == "Poor"
        assert get_eu_aqi_category(80) == "Poor"

    def test_very_poor_category(self):
        assert get_eu_aqi_category(81) == "Very Poor"
        assert get_eu_aqi_category(100) == "Very Poor"

    def test_extremely_poor_category(self):
        assert get_eu_aqi_category(101) == "Extremely Poor"
        assert get_eu_aqi_category(500) == "Extremely Poor"

    def test_real_api_value(self):
        # The actual API returned 31 for Berlin
        assert get_eu_aqi_category(31) == "Fair"
