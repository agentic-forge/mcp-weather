# mcp-weather

[![CI](https://github.com/agentic-forge/mcp-weather/actions/workflows/ci.yml/badge.svg)](https://github.com/agentic-forge/mcp-weather/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Weather MCP server using [Open-Meteo API](https://open-meteo.com/) built with [FastMCP](https://gofastmcp.com/).

## Features

- **No API key required** - Uses free Open-Meteo API
- **Smart location resolution** - City names are automatically geocoded
- **Population-based disambiguation** - When multiple cities match, picks the most likely one
- **Country filtering** - Disambiguate with "London, UK" vs "London, Canada"
- **Metric and Imperial units** - Full support for both unit systems
- **Streaming HTTP transport** - Deploy as a remote MCP server

## Tools

### `geocode`

Search for locations by city name.

```python
geocode(city="Berlin")
geocode(city="Springfield", country="US", limit=10)
```

### `get_current_weather`

Get current weather conditions.

```python
get_current_weather(city="Berlin")
get_current_weather(city="London", country="UK")
get_current_weather(latitude=52.52, longitude=13.41)
get_current_weather(city="New York", units="imperial")
```

### `get_forecast`

Get weather forecast (daily or hourly).

```python
get_forecast(city="Berlin", days=7)
get_forecast(city="Miami", units="imperial", days=5, hourly=True)
```

### `get_air_quality`

Get air quality and pollutant data.

```python
get_air_quality(city="Beijing")
get_air_quality(city="Berlin", include_pollen=True)  # Pollen: Europe only
```

## Installation

```bash
# Clone the repository
git clone https://github.com/agentic-forge/mcp-weather.git
cd mcp-weather

# Install dependencies
uv sync
```

## Running the Server

### HTTP Transport (recommended for remote access)

```bash
# Default: HTTP on port 8000
uv run python -m forge_mcp_weather

# Custom port
uv run python -m forge_mcp_weather --port 3000
```

Server will be available at `http://localhost:8000/mcp`

### STDIO Transport (for local MCP clients)

```bash
uv run python -m forge_mcp_weather --stdio
```

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["run", "python", "-m", "forge_mcp_weather", "--stdio"],
      "cwd": "/path/to/mcp-weather"
    }
  }
}
```

### Remote HTTP Server

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Type checking
uv run basedpyright

# Linting
uv run ruff check .

# Install pre-commit hooks
uv run pre-commit install
```

## Testing the Server

### Using mcp-tools-cli

[mcp-tools-cli](https://pypi.org/project/mcp-tools-cli/) is a generic MCP client for testing any MCP server.

**Install globally (once):**

```bash
uv tool install mcp-tools-cli
# or: pipx install mcp-tools-cli
```

**Create config file** (`mcp_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Usage:**

```bash
# Start the server
uv run python -m forge_mcp_weather

# List available tools
mcp-tools-cli list-tools --mcp-name weather

# Call a tool
mcp-tools-cli call-tool --mcp-name weather --tool-name get_current_weather --tool-args '{"city": "Berlin"}'
```

### Direct HTTP Testing

When running the server in HTTP mode, you can test directly with curl:

```bash
# Start the server
uv run python -m forge_mcp_weather

# List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Call get_current_weather
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_current_weather", "arguments": {"city": "Berlin"}}, "id": 1}'

# Call geocode
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "geocode", "arguments": {"city": "London", "country": "UK"}}, "id": 1}'
```

### Programmatic Testing with MCP Client

FastMCP provides a Python client that works with any MCP server (not just FastMCP servers) that supports HTTP transport:

```python
import asyncio
from fastmcp import Client

async def test_weather_server():
    async with Client("http://localhost:8000/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Get current weather
        weather = await client.call_tool(
            "get_current_weather",
            {"city": "Berlin"}
        )
        print(f"Weather: {weather}")

        # Get forecast
        forecast = await client.call_tool(
            "get_forecast",
            {"city": "Tokyo", "days": 3}
        )
        print(f"Forecast: {forecast}")

asyncio.run(test_weather_server())
```

This client can connect to any MCP server using:

- HTTP/SSE transport: `Client("http://server:port/mcp")`
- STDIO transport: `Client("uvx some-mcp-server")` or `Client(["python", "-m", "server"])`

## API Reference

This server uses the following Open-Meteo APIs:

- [Weather Forecast API](https://open-meteo.com/en/docs)
- [Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- [Geocoding API](https://open-meteo.com/en/docs/geocoding-api)

## License

MIT
