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
        calendarName: Annotated[str, "Target calendar"],
    ):
        """Creates a new calendar event"""
        client = get_client()

        calendars = client.principal().calendars()

        # Calendar selection
        if calendarName:
            calendar = next(
                (c for c in calendars if getattr(c, "name", None) == calendarName),
                None
            )
            if not calendar:
                raise ValueError(f"Calendar '{calendarName}' not found")
        else:
            if not calendars:
                raise ValueError("No calendars available")
            calendar = calendars[0]

        # Build event
        uid = str(uuid4())

        event = Event()
        event.add("uid", uid)
        event.add("summary", summary)
        event.add("dtstart", parse_dt(start))
        event.add("dtend", parse_dt(end))

        # Create event in calendar
        created = calendar.add_event(event.to_ical().decode("utf-8"))

        # Try to extract useful metadata from response
        href = getattr(created, "href", None)
        etag = getattr(created, "etag", None)

        return {
            "status": "created",
            "uid": uid,
            "summary": summary,
            "start": start,
            "end": end,
            "calendar": getattr(calendar, "name", None),
            "href": href,
            "etag": etag,
        }