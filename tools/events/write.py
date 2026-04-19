from mcp.server.fastmcp import FastMCP
from uuid import uuid4
from icalendar import Event
from typing import Annotated

from ..utils import get_client, parse_dt


def register_event_write_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_event(
        summary: Annotated[str, "Event title"],
        start: Annotated[str, "Start datetime (ISO 8601)"],
        end: Annotated[str, "End datetime (ISO 8601)"],
        calendarUrl: Annotated[str | None, "Optional target calendar URL"],
    ) -> str:
        """Creates a new calendar event and returns its URL."""
        client = get_client()

        if calendarUrl:
            calendar = client.calendar(url=calendarUrl)
        else:
            calendar = client.principal().calendars()[0]

        event = Event()
        event.add("uid", str(uuid4()))
        event.add("summary", summary)
        event.add("dtstart", parse_dt(start))
        event.add("dtend", parse_dt(end))

        created = calendar.add_event(event.to_ical().decode("utf-8"))
        return str(created.url)