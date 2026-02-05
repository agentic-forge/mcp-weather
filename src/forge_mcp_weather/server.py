"""Weather MCP Server using FastMCP and Open-Meteo API."""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from .weather.client import OpenMeteoClient
from .weather.models import (
    AirQuality,
    CurrentWeather,
    Forecast,
    Location,
)

# Path to MCP Apps directory
APPS_DIR = Path(__file__).parent.parent.parent / "apps"

# Get package version
__version__ = version("forge-mcp-weather")

# Create FastMCP server
mcp = FastMCP(
    name="Weather Server",
    version=__version__,
    instructions="""Weather information server powered by Open-Meteo API.

Available tools:
- geocode: Search for locations by city name
- get_current_weather: Get current weather conditions
- get_forecast: Get weather forecast (daily/hourly)
- get_air_quality: Get air quality and pollutant data
- pick_location: Open interactive map UI to select a location

Location can be specified by city name (with optional country) or coordinates.
When using city names, the server automatically picks the most likely match by population.

MCP Apps:
- ui://location-picker: Interactive map for selecting locations visually
""",
)

# Shared client instance
client = OpenMeteoClient()


@mcp.tool
async def geocode(
    city: Annotated[str, Field(description="City name to search (e.g., 'Berlin', 'New York')")],
    country: Annotated[
        str | None,
        Field(description="Country name or code to filter results (e.g., 'Germany', 'DE', 'US')"),
    ] = None,
    limit: Annotated[
        int,
        Field(ge=1, le=10, description="Maximum number of results to return"),
    ] = 5,
) -> list[Location]:
    """Search for locations by city name.

    Returns a list of matching locations with coordinates, sorted by population.
    Use this to find the exact coordinates of a city before querying weather data,
    or to disambiguate cities with common names (e.g., 'Springfield', 'London').
    """
    return await client.geocode(city, country, limit)


@mcp.tool
async def get_current_weather(
    city: Annotated[
        str | None,
        Field(description="City name (e.g., 'Berlin', 'Tokyo')"),
    ] = None,
    country: Annotated[
        str | None,
        Field(description="Country name or code (e.g., 'Germany', 'JP')"),
    ] = None,
    latitude: Annotated[
        float | None,
        Field(ge=-90, le=90, description="Latitude coordinate"),
    ] = None,
    longitude: Annotated[
        float | None,
        Field(ge=-180, le=180, description="Longitude coordinate"),
    ] = None,
    units: Annotated[
        Literal["metric", "imperial"],
        Field(description="Unit system: 'metric' (°C, km/h) or 'imperial' (°F, mph)"),
    ] = "metric",
) -> CurrentWeather:
    """Get current weather conditions for a location.

    Provide either:
    - city (optionally with country for disambiguation), OR
    - latitude and longitude coordinates

    Examples:
    - get_current_weather(city="Berlin")
    - get_current_weather(city="London", country="UK")
    - get_current_weather(latitude=52.52, longitude=13.41)
    - get_current_weather(city="New York", units="imperial")
    """
    return await client.get_current_weather(city, country, latitude, longitude, units)


@mcp.tool
async def get_forecast(
    city: Annotated[
        str | None,
        Field(description="City name (e.g., 'Paris', 'Sydney')"),
    ] = None,
    country: Annotated[
        str | None,
        Field(description="Country name or code (e.g., 'France', 'AU')"),
    ] = None,
    latitude: Annotated[
        float | None,
        Field(ge=-90, le=90, description="Latitude coordinate"),
    ] = None,
    longitude: Annotated[
        float | None,
        Field(ge=-180, le=180, description="Longitude coordinate"),
    ] = None,
    days: Annotated[
        int,
        Field(ge=1, le=16, description="Number of forecast days (1-16)"),
    ] = 7,
    hourly: Annotated[
        bool,
        Field(description="Include hourly breakdown in addition to daily forecast"),
    ] = False,
    units: Annotated[
        Literal["metric", "imperial"],
        Field(description="Unit system: 'metric' (°C, km/h) or 'imperial' (°F, mph)"),
    ] = "metric",
) -> Forecast:
    """Get weather forecast for a location.

    Returns daily forecast by default. Set hourly=True for hourly breakdown.

    Examples:
    - get_forecast(city="Berlin", days=7)
    - get_forecast(city="Miami", units="imperial", days=5)
    - get_forecast(latitude=48.85, longitude=2.35, hourly=True)
    """
    return await client.get_forecast(city, country, latitude, longitude, days, hourly, units)


@mcp.tool
async def get_air_quality(
    city: Annotated[
        str | None,
        Field(description="City name (e.g., 'Beijing', 'Los Angeles')"),
    ] = None,
    country: Annotated[
        str | None,
        Field(description="Country name or code (e.g., 'China', 'US')"),
    ] = None,
    latitude: Annotated[
        float | None,
        Field(ge=-90, le=90, description="Latitude coordinate"),
    ] = None,
    longitude: Annotated[
        float | None,
        Field(ge=-180, le=180, description="Longitude coordinate"),
    ] = None,
    include_pollen: Annotated[
        bool,
        Field(description="Include pollen data (only available for European locations)"),
    ] = False,
) -> AirQuality:
    """Get air quality and pollutant data for a location.

    Returns:
    - US EPA Air Quality Index (AQI) with category
    - European Air Quality Index with category
    - Pollutant concentrations (PM2.5, PM10, O3, NO2, SO2, CO)
    - Pollen levels (Europe only, if include_pollen=True)

    Examples:
    - get_air_quality(city="Beijing")
    - get_air_quality(city="Berlin", include_pollen=True)
    - get_air_quality(latitude=34.05, longitude=-118.24)
    """
    return await client.get_air_quality(city, country, latitude, longitude, include_pollen)


# =============================================================================
# MCP Apps - Interactive UI Components
# =============================================================================


@mcp.resource("ui://location-picker")
async def location_picker_ui() -> str:
    """Interactive map for picking a location.

    Returns a bundled HTML/JS application that displays an interactive
    Leaflet map. Users can click to select a location or search for cities.
    """
    ui_path = APPS_DIR / "location-picker" / "dist" / "index.html"
    if not ui_path.exists():
        raise FileNotFoundError(
            f"Location picker app not built. Run 'bun run build' in {APPS_DIR / 'location-picker'}"
        )
    return ui_path.read_text()


@mcp.tool
async def pick_location(
    initial_lat: Annotated[
        float | None,
        Field(ge=-90, le=90, description="Initial latitude to center the map"),
    ] = None,
    initial_lng: Annotated[
        float | None,
        Field(ge=-180, le=180, description="Initial longitude to center the map"),
    ] = None,
    initial_city: Annotated[
        str | None,
        Field(description="Initial city name to center the map (alternative to coordinates)"),
    ] = None,
) -> dict:
    """Open interactive map to pick a location.

    Returns an interactive map where the user can click to select
    a location or search for a city. The selected coordinates will
    be available for subsequent weather queries.

    Use this tool when:
    - The user wants to visually select a location on a map
    - The user is unsure of exact coordinates
    - You need to help the user choose from nearby locations
    """
    initial_location = None

    # If city provided, geocode it first
    if initial_city:
        locations = await client.geocode(initial_city, None, 1)
        if locations:
            loc = locations[0]
            initial_location = {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "name": loc.name,
                "country": loc.country,
            }
    elif initial_lat is not None and initial_lng is not None:
        initial_location = {
            "latitude": initial_lat,
            "longitude": initial_lng,
        }

    return {
        "_meta": {
            "ui": {
                "resourceUri": "ui://location-picker",
                "permissions": ["geolocation"],  # For "Use My Location" button
                "requiresInteraction": True,
            }
        },
        "initial_location": initial_location,
        "instructions": "Click on the map or search for a city to select a location. "
        "The selected location will be available for weather queries.",
    }


def main():
    """Run the weather MCP server."""
    import argparse
    import logging
    import warnings

    import uvicorn
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    # Suppress websockets deprecation warnings from uvicorn
    # These are from uvicorn's websocket protocol using deprecated websockets APIs
    # See: https://websockets.readthedocs.io/en/stable/howto/upgrade.html
    warnings.filterwarnings("ignore", message="websockets.legacy is deprecated")
    warnings.filterwarnings(
        "ignore", message="websockets.server.WebSocketServerProtocol is deprecated"
    )

    # Suppress benign ClosedResourceError on client disconnect
    # This is a known issue in MCP SDK: https://github.com/jlowin/fastmcp/issues/2083
    logging.getLogger("mcp.server.streamable_http").setLevel(logging.CRITICAL)

    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Use STDIO transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP transport")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    if args.stdio:
        mcp.run(transport="stdio")
    else:
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        # Add CORS middleware for browser-based clients
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=["*"],
                expose_headers=["mcp-session-id"],
            )
        ]
        app = mcp.http_app(middleware=middleware)

        # Add health check endpoint for Docker healthchecks
        async def health_check(_request):
            return JSONResponse({"status": "healthy", "service": "mcp-weather"})

        app.routes.append(Route("/health", health_check))

        print(f"Starting Weather MCP Server on http://{args.host}:{args.port}/mcp")
        if args.reload:
            # For reload mode, use app string path
            uvicorn.run(
                "forge_mcp_weather.server:create_app",
                factory=True,
                host=args.host,
                port=args.port,
                reload=True,
            )
        else:
            uvicorn.run(app, host=args.host, port=args.port)


def create_app():
    """Factory function for uvicorn reload mode."""
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id"],
        )
    ]
    app = mcp.http_app(middleware=middleware)

    async def health_check(_request):
        return JSONResponse({"status": "healthy", "service": "mcp-weather"})

    app.routes.append(Route("/health", health_check))
    return app


if __name__ == "__main__":
    main()
