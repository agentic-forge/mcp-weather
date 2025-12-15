"""Unit conversion utilities for weather data."""


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


def kmh_to_mph(kmh: float) -> float:
    """Convert wind speed from km/h to mph."""
    return kmh * 0.621371


def mph_to_kmh(mph: float) -> float:
    """Convert wind speed from mph to km/h."""
    return mph / 0.621371


def hpa_to_inhg(hpa: float) -> float:
    """Convert pressure from hPa (hectopascals) to inches of mercury."""
    return hpa * 0.02953


def inhg_to_hpa(inhg: float) -> float:
    """Convert pressure from inches of mercury to hPa."""
    return inhg / 0.02953


def mm_to_inches(mm: float) -> float:
    """Convert precipitation from millimeters to inches."""
    return mm * 0.0393701


def inches_to_mm(inches: float) -> float:
    """Convert precipitation from inches to millimeters."""
    return inches / 0.0393701


def degrees_to_compass(degrees: int) -> str:
    """Convert wind direction from degrees to 16-point compass direction.

    Args:
        degrees: Wind direction in degrees (0-360, where 0/360 is North)

    Returns:
        16-point compass direction (N, NNE, NE, ENE, E, etc.)
    """
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    # Normalize degrees to 0-360 range
    degrees = degrees % 360
    # Each direction covers 22.5 degrees (360/16)
    index = round(degrees / 22.5) % 16
    return directions[index]
