from mcp.server.fastmcp import FastMCP
from typing import Annotated
from ..utils import get_client, getLogger


def register_calendar_read_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_calendars() -> list[dict]:
        """Lists all available calendars."""
        
        getLogger().info("Executing list_calendars.")
        
        client = get_client()
        calendars = client.principal().calendars()

        return [
            {"name": c.name, "url": str(c.url)}
            for c in calendars
        ]