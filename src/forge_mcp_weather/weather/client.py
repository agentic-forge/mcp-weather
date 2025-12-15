"""Open-Meteo API client for weather, air quality, and geocoding data."""

from typing import Literal

import httpx

from .constants import get_eu_aqi_category, get_us_aqi_category, get_weather_description
from .conversions import degrees_to_compass
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


def _safe_get[T](data: dict, key: str, index: int, default: T) -> T:
    """Safely get a value from a list in a dict at the given index."""
    values = data.get(key, [])
    if index < len(values):
        return values[index]
    return default


class WeatherError(Exception):
    """Base exception for weather server errors."""

    pass


class LocationNotFoundError(WeatherError):
    """No matching location found for the given query."""

    pass


class APIError(WeatherError):
    """Error from Open-Meteo API."""

    pass


class OpenMeteoClient:
    """Async client for Open-Meteo APIs."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(self, timeout: float = 30.0):
        """Initialize the client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def _request(self, url: str, params: dict) -> dict:
        """Make an async HTTP request to Open-Meteo API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code} {response.text}")
            return response.json()

    async def geocode(
        self,
        city: str,
        country: str | None = None,
        limit: int = 5,
    ) -> list[Location]:
        """Search for locations by city name.

        Args:
            city: City name to search
            country: Optional country name or code to filter results
            limit: Maximum number of results (1-10)

        Returns:
            List of matching locations sorted by population (highest first)
        """
        params = {
            "name": city,
            "count": min(max(limit, 1), 10),
            "language": "en",
            "format": "json",
        }

        data = await self._request(self.GEOCODING_URL, params)
        results = data.get("results", [])

        if not results:
            return []

        locations = []
        for r in results:
            loc = Location(
                name=r.get("name", ""),
                country=r.get("country", ""),
                country_code=r.get("country_code", ""),
                latitude=r.get("latitude", 0),
                longitude=r.get("longitude", 0),
                timezone=r.get("timezone", "UTC"),
                population=r.get("population"),
                admin1=r.get("admin1"),
            )
            locations.append(loc)

        # Filter by country if specified
        if country:
            country_lower = country.lower()
            filtered = [
                loc
                for loc in locations
                if country_lower in (loc.country.lower(), loc.country_code.lower())
            ]
            if filtered:
                locations = filtered

        # Sort by population (highest first), handling None values
        locations.sort(key=lambda x: x.population or 0, reverse=True)

        return locations

    async def resolve_location(
        self,
        city: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> tuple[float, float, str]:
        """Resolve location input to coordinates and display name.

        Args:
            city: City name
            country: Country name or code
            latitude: Direct latitude coordinate
            longitude: Direct longitude coordinate

        Returns:
            Tuple of (latitude, longitude, display_name)

        Raises:
            WeatherError: If neither coordinates nor city name provided
            LocationNotFoundError: If city not found
        """
        # If coordinates provided, use them directly
        if latitude is not None and longitude is not None:
            return (latitude, longitude, f"{latitude:.4f}, {longitude:.4f}")

        # Must have city name
        if not city:
            raise WeatherError("Provide either city name or latitude/longitude coordinates")

        # Geocode the city
        locations = await self.geocode(city, country)

        if not locations:
            raise LocationNotFoundError(f"No location found for '{city}'")

        # Pick the best match (already sorted by population)
        best = locations[0]
        display_name = f"{best.name}, {best.country}"

        return (best.latitude, best.longitude, display_name)

    async def get_current_weather(
        self,
        city: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        units: Literal["metric", "imperial"] = "metric",
    ) -> CurrentWeather:
        """Get current weather conditions.

        Args:
            city: City name (e.g., "Berlin")
            country: Country name or code (e.g., "Germany", "DE")
            latitude: Direct latitude coordinate
            longitude: Direct longitude coordinate
            units: Unit system ("metric" or "imperial")

        Returns:
            Current weather conditions
        """
        lat, lon, location_name = await self.resolve_location(city, country, latitude, longitude)

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "pressure_msl",
                ]
            ),
            "timezone": "auto",
        }

        # Set units based on preference
        if units == "imperial":
            params["temperature_unit"] = "fahrenheit"
            params["wind_speed_unit"] = "mph"
            params["precipitation_unit"] = "inch"

        data = await self._request(self.FORECAST_URL, params)
        current = data.get("current", {})

        weather_code = current.get("weather_code", 0)
        wind_dir = current.get("wind_direction_10m", 0)

        # Determine unit labels
        if units == "imperial":
            weather_units = WeatherUnits(
                temperature="°F",
                wind_speed="mph",
                pressure="hPa",  # Open-Meteo doesn't convert pressure
                precipitation="in",
            )
        else:
            weather_units = WeatherUnits(
                temperature="°C",
                wind_speed="km/h",
                pressure="hPa",
                precipitation="mm",
            )

        return CurrentWeather(
            location=location_name,
            coordinates=(lat, lon),
            timezone=data.get("timezone", "UTC"),
            time=current.get("time", ""),
            temperature=current.get("temperature_2m", 0),
            feels_like=current.get("apparent_temperature", 0),
            humidity=current.get("relative_humidity_2m", 0),
            weather_code=weather_code,
            weather_description=get_weather_description(weather_code),
            wind_speed=current.get("wind_speed_10m", 0),
            wind_direction=wind_dir,
            wind_direction_compass=degrees_to_compass(wind_dir),
            pressure=current.get("pressure_msl", 0),
            units=weather_units,
        )

    async def get_forecast(
        self,
        city: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        days: int = 7,
        hourly: bool = False,
        units: Literal["metric", "imperial"] = "metric",
    ) -> Forecast:
        """Get weather forecast.

        Args:
            city: City name
            country: Country name or code
            latitude: Direct latitude coordinate
            longitude: Direct longitude coordinate
            days: Number of forecast days (1-16)
            hourly: Include hourly breakdown
            units: Unit system ("metric" or "imperial")

        Returns:
            Weather forecast
        """
        lat, lon, location_name = await self.resolve_location(city, country, latitude, longitude)

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "weather_code",
                    "sunrise",
                    "sunset",
                    "wind_speed_10m_max",
                ]
            ),
            "timezone": "auto",
            "forecast_days": min(max(days, 1), 16),
        }

        if hourly:
            params["hourly"] = ",".join(
                [
                    "temperature_2m",
                    "precipitation_probability",
                    "weather_code",
                    "wind_speed_10m",
                ]
            )

        if units == "imperial":
            params["temperature_unit"] = "fahrenheit"
            params["wind_speed_unit"] = "mph"
            params["precipitation_unit"] = "inch"

        data = await self._request(self.FORECAST_URL, params)

        # Determine unit labels
        if units == "imperial":
            weather_units = WeatherUnits(
                temperature="°F",
                wind_speed="mph",
                pressure="hPa",
                precipitation="in",
            )
        else:
            weather_units = WeatherUnits(
                temperature="°C",
                wind_speed="km/h",
                pressure="hPa",
                precipitation="mm",
            )

        # Parse daily forecasts
        daily_data = data.get("daily", {})
        daily_forecasts = []

        dates = daily_data.get("time", [])
        for i, date in enumerate(dates):
            weather_code = _safe_get(daily_data, "weather_code", i, 0)

            # Extract sunrise/sunset times (remove date part)
            sunrise_full = _safe_get(daily_data, "sunrise", i, "")
            sunset_full = _safe_get(daily_data, "sunset", i, "")
            sunrise = sunrise_full.split("T")[1] if "T" in sunrise_full else sunrise_full
            sunset = sunset_full.split("T")[1] if "T" in sunset_full else sunset_full

            precip_prob = _safe_get(daily_data, "precipitation_probability_max", i, 0)
            daily_forecasts.append(
                DailyForecast(
                    date=date,
                    temperature_max=_safe_get(daily_data, "temperature_2m_max", i, 0),
                    temperature_min=_safe_get(daily_data, "temperature_2m_min", i, 0),
                    feels_like_max=_safe_get(daily_data, "apparent_temperature_max", i, 0),
                    feels_like_min=_safe_get(daily_data, "apparent_temperature_min", i, 0),
                    precipitation_sum=_safe_get(daily_data, "precipitation_sum", i, 0),
                    precipitation_probability=precip_prob,
                    weather_code=weather_code,
                    weather_description=get_weather_description(weather_code),
                    sunrise=sunrise,
                    sunset=sunset,
                    wind_speed_max=_safe_get(daily_data, "wind_speed_10m_max", i, 0),
                )
            )

        # Parse hourly forecasts if requested
        hourly_forecasts = None
        if hourly:
            hourly_data = data.get("hourly", {})
            hourly_forecasts = []

            times = hourly_data.get("time", [])
            for i, time in enumerate(times):
                weather_code = _safe_get(hourly_data, "weather_code", i, 0)
                precip_prob = _safe_get(hourly_data, "precipitation_probability", i, 0)

                hourly_forecasts.append(
                    HourlyForecast(
                        time=time,
                        temperature=_safe_get(hourly_data, "temperature_2m", i, 0),
                        precipitation_probability=precip_prob,
                        weather_code=weather_code,
                        weather_description=get_weather_description(weather_code),
                        wind_speed=_safe_get(hourly_data, "wind_speed_10m", i, 0),
                    )
                )

        return Forecast(
            location=location_name,
            coordinates=(lat, lon),
            timezone=data.get("timezone", "UTC"),
            units=weather_units,
            daily=daily_forecasts,
            hourly=hourly_forecasts,
        )

    async def get_air_quality(
        self,
        city: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        include_pollen: bool = False,
    ) -> AirQuality:
        """Get air quality data.

        Args:
            city: City name
            country: Country name or code
            latitude: Direct latitude coordinate
            longitude: Direct longitude coordinate
            include_pollen: Include pollen data (Europe only)

        Returns:
            Air quality data
        """
        lat, lon, location_name = await self.resolve_location(city, country, latitude, longitude)

        current_params = [
            "us_aqi",
            "european_aqi",
            "pm10",
            "pm2_5",
            "carbon_monoxide",
            "nitrogen_dioxide",
            "sulphur_dioxide",
            "ozone",
        ]

        if include_pollen:
            current_params.extend(
                [
                    "alder_pollen",
                    "birch_pollen",
                    "grass_pollen",
                    "mugwort_pollen",
                    "olive_pollen",
                    "ragweed_pollen",
                ]
            )

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join(current_params),
            "timezone": "auto",
        }

        data = await self._request(self.AIR_QUALITY_URL, params)
        current = data.get("current", {})

        us_aqi_value = current.get("us_aqi", 0) or 0
        eu_aqi_value = current.get("european_aqi", 0) or 0

        # Build pollen data if requested
        pollen = None
        if include_pollen:
            pollen = PollenLevels(
                alder=current.get("alder_pollen", 0) or 0,
                birch=current.get("birch_pollen", 0) or 0,
                grass=current.get("grass_pollen", 0) or 0,
                mugwort=current.get("mugwort_pollen", 0) or 0,
                olive=current.get("olive_pollen", 0) or 0,
                ragweed=current.get("ragweed_pollen", 0) or 0,
            )

        return AirQuality(
            location=location_name,
            coordinates=(lat, lon),
            time=current.get("time", ""),
            us_aqi=AirQualityIndex(
                value=us_aqi_value,
                category=get_us_aqi_category(us_aqi_value),
            ),
            european_aqi=AirQualityIndex(
                value=eu_aqi_value,
                category=get_eu_aqi_category(eu_aqi_value),
            ),
            pollutants=Pollutants(
                pm2_5=current.get("pm2_5", 0) or 0,
                pm10=current.get("pm10", 0) or 0,
                ozone=current.get("ozone", 0) or 0,
                nitrogen_dioxide=current.get("nitrogen_dioxide", 0) or 0,
                sulphur_dioxide=current.get("sulphur_dioxide", 0) or 0,
                carbon_monoxide=current.get("carbon_monoxide", 0) or 0,
            ),
            pollen=pollen,
        )
