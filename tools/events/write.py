from mcp.server.fastmcp import FastMCP
from uuid import uuid4
from icalendar import Event
from typing import Annotated

from ..utils import get_client, parse_dt, getLogger


def register_event_write_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_event(
        summary: Annotated[str, "Event title"],
        start: Annotated[str, "Start datetime (ISO 8601)"],
        end: Annotated[str, "End datetime (ISO 8601)"],
        calendarName: Annotated[str, "Target calendar"],
    ):
        """Creates a new calendar event"""#
        
        getLogger().info("Executing create_event.")
        
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
        
        
    @mcp.tool()
    async def delete_event(
        uid: Annotated[str, "UID of the event to delete"],
        calendarName: Annotated[
            str | None,
            "Optional target calendar name. If omitted, all calendars are searched."
        ] = None,
    ) -> dict:
        """Deletes an event by UID."""

        getLogger().info(
            "Executing delete_event for uid='%s', calendar='%s'.",
            uid,
            calendarName or "all",
        )

        if not uid or not uid.strip():
            raise ValueError("Event UID must not be empty")

        client = get_client()
        calendars = client.principal().calendars()

        if not calendars:
            raise ValueError("No calendars available")

        # Select calendars
        if calendarName:
            calendars_to_search = [
                c for c in calendars
                if getattr(c, "name", None) == calendarName
            ]

            if not calendars_to_search:
                raise ValueError(f"Calendar '{calendarName}' not found")
        else:
            calendars_to_search = calendars

        matches = []

        # Search event in selected calendars
        for calendar in calendars_to_search:
            calendar_name = getattr(calendar, "name", "Unknown")

            getLogger().debug(
                "Searching for event '%s' in calendar '%s'.",
                uid,
                calendar_name,
            )

            events = calendar.events()

            for event in events:
                vevent = event.vobject_instance.vevent

                event_uid = str(
                    getattr(vevent, "uid", "")
                )

                if event_uid == uid:
                    matches.append(
                        (calendar, event, calendar_name, vevent)
                    )

        if not matches:
            raise ValueError(f"Event with UID '{uid}' not found")

        # Prevent accidentally deleting multiple events
        if len(matches) > 1:
            calendars_found = [
                match[2] for match in matches
            ]

            raise ValueError(
                f"Event with UID '{uid}' exists in multiple calendars: "
                f"{', '.join(calendars_found)}. "
                f"Specify calendarName explicitly."
            )

        calendar, event, calendar_name, vevent = matches[0]

        summary = str(
            getattr(vevent, "summary", "No Title")
        )

        getLogger().info(
            "Deleting event '%s' (%s) from calendar '%s'.",
            summary,
            uid,
            calendar_name,
        )

        event.delete()

        return {
            "success": True,
            "uid": uid,
            "calendar": calendar_name,
            "summary": summary,
        }
