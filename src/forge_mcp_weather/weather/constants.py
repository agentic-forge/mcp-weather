"""Weather codes and AQI category constants."""

# WMO Weather interpretation codes (WW)
# https://open-meteo.com/en/docs
WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# US EPA Air Quality Index categories
# https://www.airnow.gov/aqi/aqi-basics/
US_AQI_CATEGORIES: dict[tuple[int, int], str] = {
    (0, 50): "Good",
    (51, 100): "Moderate",
    (101, 150): "Unhealthy for Sensitive Groups",
    (151, 200): "Unhealthy",
    (201, 300): "Very Unhealthy",
    (301, 500): "Hazardous",
}

# European Air Quality Index categories
EU_AQI_CATEGORIES: dict[tuple[int, int], str] = {
    (0, 20): "Good",
    (21, 40): "Fair",
    (41, 60): "Moderate",
    (61, 80): "Poor",
    (81, 100): "Very Poor",
    (101, 999): "Extremely Poor",
}


def get_weather_description(code: int) -> str:
    """Get human-readable description for a WMO weather code."""
    return WEATHER_CODES.get(code, f"Unknown ({code})")


def get_us_aqi_category(aqi: int) -> str:
    """Get US EPA AQI category for a given AQI value."""
    for (low, high), category in US_AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return category
    return "Unknown"


def get_eu_aqi_category(aqi: int) -> str:
    """Get European AQI category for a given AQI value."""
    for (low, high), category in EU_AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return category
    return "Unknown"
