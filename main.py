import logging
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import register_tools

load_dotenv()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("mcp-server")


mcp = FastMCP(
    name="caldav-server",
    host="0.0.0.0",
    port=8123
)

logger.info("Starting MCP server...")


# Tools registrieren
register_tools(mcp)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        mount_path="/mcp",
    )