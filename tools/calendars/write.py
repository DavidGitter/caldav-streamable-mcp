from mcp.server.fastmcp import FastMCP
from typing import Annotated
from ..utils import get_client, getLogger


def register_calendar_write_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_calendar(
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> dict:
        """Creates a new calendar."""

        getLogger().info("Executing create_calendar.")

        try:
            client = get_client()
            principal = client.principal()

            calendar = principal.make_calendar(name=name)

        except Exception as err:
            getLogger().exception(err)
    
        return {
            "success": True,
            "name": name,
        }
        
        
    @mcp.tool()
    async def delete_calendar(
        name: str,
    ) -> dict:
        """Deletes a calendar by name."""

        getLogger().info("Executing delete_calendar for '%s'.", name)

        if not name or not name.strip():
            raise ValueError("Calendar name must not be empty")

        try:
            client = get_client()
            principal = client.principal()

            calendars = principal.calendars()

            # Find calendar by name
            calendar = next(
                (
                    c for c in calendars
                    if getattr(c, "name", None) == name
                ),
                None
            )

            if not calendar:
                raise ValueError(f"Calendar '{name}' not found")

            getLogger().info(
                "Deleting calendar '%s' (%s).",
                name,
                getattr(calendar, "url", "unknown URL"),
            )

            calendar.delete()

            return {
                "success": True,
                "name": name,
            }

        except Exception:
            getLogger().exception(
                "Failed to delete calendar '%s'.",
                name,
            )
            raise
