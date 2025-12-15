"""Pydantic models for weather data responses."""

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Geocoded location information."""

    name: str = Field(description="City name")
    country: str = Field(description="Country name")
    country_code: str = Field(description="ISO country code (e.g., 'DE', 'US')")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    timezone: str = Field(description="IANA timezone (e.g., 'Europe/Berlin')")
    population: int | None = Field(default=None, description="City population")
    admin1: str | None = Field(default=None, description="State/province/region name")


class WeatherUnits(BaseModel):
    """Unit labels for weather measurements."""

    temperature: str = Field(description="Temperature unit (e.g., '°C', '°F')")
    wind_speed: str = Field(description="Wind speed unit (e.g., 'km/h', 'mph')")
    pressure: str = Field(description="Pressure unit (e.g., 'hPa', 'inHg')")
    precipitation: str = Field(description="Precipitation unit (e.g., 'mm', 'in')")


class CurrentWeather(BaseModel):
    """Current weather conditions."""

    location: str = Field(description="Location display name (e.g., 'Berlin, Germany')")
    coordinates: tuple[float, float] = Field(description="(latitude, longitude)")
    timezone: str = Field(description="IANA timezone")
    time: str = Field(description="Observation time (ISO format)")

    temperature: float = Field(description="Current temperature")
    feels_like: float = Field(description="Apparent temperature")
    humidity: int = Field(description="Relative humidity (%)")

    weather_code: int = Field(description="WMO weather code")
    weather_description: str = Field(description="Human-readable weather description")

    wind_speed: float = Field(description="Wind speed")
    wind_direction: int = Field(description="Wind direction (degrees)")
    wind_direction_compass: str = Field(description="Wind direction (compass, e.g., 'NNE')")

    pressure: float = Field(description="Sea level pressure")

    units: WeatherUnits = Field(description="Units for measurements")


class DailyForecast(BaseModel):
    """Daily weather forecast."""

    date: str = Field(description="Forecast date (YYYY-MM-DD)")
    temperature_max: float = Field(description="Maximum temperature")
    temperature_min: float = Field(description="Minimum temperature")
    feels_like_max: float = Field(description="Maximum apparent temperature")
    feels_like_min: float = Field(description="Minimum apparent temperature")
    precipitation_sum: float = Field(description="Total precipitation")
    precipitation_probability: int = Field(description="Precipitation probability (%)")
    weather_code: int = Field(description="WMO weather code")
    weather_description: str = Field(description="Human-readable weather description")
    sunrise: str = Field(description="Sunrise time (HH:MM)")
    sunset: str = Field(description="Sunset time (HH:MM)")
    wind_speed_max: float = Field(description="Maximum wind speed")


class HourlyForecast(BaseModel):
    """Hourly weather forecast."""

    time: str = Field(description="Forecast time (ISO format)")
    temperature: float = Field(description="Temperature")
    precipitation_probability: int = Field(description="Precipitation probability (%)")
    weather_code: int = Field(description="WMO weather code")
    weather_description: str = Field(description="Human-readable weather description")
    wind_speed: float = Field(description="Wind speed")


class Forecast(BaseModel):
    """Weather forecast response."""

    location: str = Field(description="Location display name")
    coordinates: tuple[float, float] = Field(description="(latitude, longitude)")
    timezone: str = Field(description="IANA timezone")
    units: WeatherUnits = Field(description="Units for measurements")
    daily: list[DailyForecast] = Field(description="Daily forecasts")
    hourly: list[HourlyForecast] | None = Field(
        default=None, description="Hourly forecasts (if requested)"
    )


class AirQualityIndex(BaseModel):
    """Air quality index value with category."""

    value: int = Field(description="AQI numeric value")
    category: str = Field(description="AQI category (e.g., 'Good', 'Moderate')")


class Pollutants(BaseModel):
    """Pollutant concentration levels (μg/m³)."""

    pm2_5: float = Field(description="Fine particulate matter (PM2.5)")
    pm10: float = Field(description="Coarse particulate matter (PM10)")
    ozone: float = Field(description="Ozone (O3)")
    nitrogen_dioxide: float = Field(description="Nitrogen dioxide (NO2)")
    sulphur_dioxide: float = Field(description="Sulphur dioxide (SO2)")
    carbon_monoxide: float = Field(description="Carbon monoxide (CO)")


class PollenLevels(BaseModel):
    """Pollen concentration levels (grains/m³). Europe only."""

    alder: float = Field(description="Alder pollen")
    birch: float = Field(description="Birch pollen")
    grass: float = Field(description="Grass pollen")
    mugwort: float = Field(description="Mugwort pollen")
    olive: float = Field(description="Olive pollen")
    ragweed: float = Field(description="Ragweed pollen")


class AirQuality(BaseModel):
    """Air quality data response."""

    location: str = Field(description="Location display name")
    coordinates: tuple[float, float] = Field(description="(latitude, longitude)")
    time: str = Field(description="Observation time (ISO format)")

    us_aqi: AirQualityIndex = Field(description="US EPA Air Quality Index")
    european_aqi: AirQualityIndex = Field(description="European Air Quality Index")

    pollutants: Pollutants = Field(description="Pollutant concentrations")
    pollen: PollenLevels | None = Field(
        default=None, description="Pollen levels (Europe only, if requested)"
    )
