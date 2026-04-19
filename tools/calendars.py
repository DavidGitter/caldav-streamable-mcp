from mcp.server.fastmcp import FastMCP
from .utils import get_client

def register_calendar_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_calendars():
        """Lists all available calendars."""
        client = get_client()
        calendars = client.principal().calendars()

        return [
            {"name": c.name, "url": str(c.url)}
            for c in calendars
        ]