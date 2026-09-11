import logging
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from tools import register_tools

from tools import utils

load_dotenv()

mcp = FastMCP(
    name="caldav-server",
    host="0.0.0.0",
    port=8123
)

@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    return JSONResponse({"status": "healthy"})


utils.getLogger().info("Starting MCP server...")

# registering the tools in ./tools
register_tools(mcp)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        mount_path="/mcp",
    )