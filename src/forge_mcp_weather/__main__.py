"""Entry point for running the Weather MCP server as a module.

Usage:
    uv run python -m forge_mcp_weather              # HTTP on port 8000
    uv run python -m forge_mcp_weather --stdio      # STDIO transport
    uv run python -m forge_mcp_weather --port=3000  # HTTP on port 3000
"""

from .server import main

if __name__ == "__main__":
    main()
