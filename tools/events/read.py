from mcp.server.fastmcp import FastMCP
from datetime import timezone
from typing import Annotated

from ..utils import get_client, parse_dt


from mcp.server.fastmcp import FastMCP
from typing import Annotated

from ..utils import get_client, parse_dt, getLogger, get_vobject_value


def register_event_read_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_events_between(
        start: Annotated[str, "Start datetime (ISO 8601)"],
        end: Annotated[str, "End datetime (ISO 8601)"],
        calendarName: Annotated[str, "Target calendar name"],
    ) -> list[dict]:
        """Lists events within a timeframe for one calendar."""
        
        getLogger().info("Executing list_events.")
        
        client = get_client()

        calendars = client.principal().calendars()

        # Find calendar by name
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

        # Query events
        events = calendar.date_search(
            start=parse_dt(start),
            end=parse_dt(end)
        )

        result = []
        for e in events:
            vevent = e.vobject_instance.vevent

            result.append({
                "uid": get_vobject_value(vevent, "uid", "n/a"),
                "summary": get_vobject_value(vevent, "summary", "No Title"),
                "start": get_vobject_value(vevent.dtstart, "value", ""),
                "end": get_vobject_value(vevent.dtend, "value", ""),
            })

        return result


    @mcp.tool()
    async def list_all_events(
        start: Annotated[str, "Start datetime (ISO 8601)"],
        end: Annotated[str, "End datetime (ISO 8601)"],
    ) -> list[dict]:
        """Lists events across all calendars within a timeframe."""
        
        getLogger().info("Executing list_all_events.")
        
        client = get_client()
        calendars = client.principal().calendars()

        dtstart = parse_dt(start)
        dtend = parse_dt(end)

        if dtstart.tzinfo is None:
            dtstart = dtstart.replace(tzinfo=timezone.utc)
        if dtend.tzinfo is None:
            dtend = dtend.replace(tzinfo=timezone.utc)

        result = []

        def safe_get(obj, attr):
            try:
                val = getattr(obj, attr, None)
                return getattr(val, "value", None) if val else None
            except Exception:
                return None

        for calendar in calendars:
            try:
                events = calendar.search(
                    start=dtstart,
                    end=dtend,
                    event=True,
                    expand=True
                )

                for e in events:
                    vevent = e.vobject_instance.vevent

                    result.append({
                        "calendar": str(calendar.name),
                        "calendarUrl": str(calendar.url),
                        "uid": get_vobject_value(vevent, "uid", "n/a"),
                        "summary": get_vobject_value(vevent, "summary", "No Title"),
                        "start": str(safe_get(vevent, "dtstart")),
                        "end": str(safe_get(vevent, "dtend")),
                        "allDay": safe_get(vevent, "dtend") is None
                    })

            except Exception as err:
                getLogger().exception(err)
                result.append({
                    "calendar": str(calendar.name),
                    "error": str(err)
                })

        return result
    
    
    @mcp.tool()
    async def list_day_events(
        date: Annotated[str, "Date (YYYY-MM-DD)"],
        calendarName: Annotated[
            str | None,
            "Optional target calendar name. If omitted, all calendars are searched."
        ] = None,
    ) -> list[dict]:
        """Lists all events for one calendar day."""

        getLogger().info(
            "Executing list_day_events for %s, calendar=%s.",
            date,
            calendarName or "all",
        )

        client = get_client()
        calendars = client.principal().calendars()

        if not calendars:
            raise ValueError("No calendars available")

        # Find calendar(s) by name
        if calendarName:
            calendars_to_search = [
                c for c in calendars
                if getattr(c, "name", None) == calendarName
            ]

            if not calendars_to_search:
                raise ValueError(f"Calendar '{calendarName}' not found")
        else:
            # No calendar specified -> search all calendars
            calendars_to_search = calendars

        # Create start/end of the requested day
        start = parse_dt(f"{date}T00:00:00")
        end = parse_dt(f"{date}T23:59:59")

        result = []

        # Search all selected calendars
        for calendar in calendars_to_search:
            calendar_name = getattr(calendar, "name", "Unknown")

            getLogger().debug(
                "Searching calendar '%s'.",
                calendar_name,
            )

            events = calendar.date_search(
                start=start,
                end=end,
            )

            for e in events:
                vevent = e.vobject_instance.vevent

                result.append({
                    "calendar": calendar_name,
                    "uid": get_vobject_value(vevent, "uid", "n/a"),
                    "summary": str(
                        getattr(vevent, "summary", "No Title")
                    ),
                    "start": str(
                        getattr(vevent.dtstart, "value", "")
                    ),
                    "end": str(
                        getattr(
                            getattr(vevent, "dtend", None),
                            "value",
                            ""
                        )
                    ),
                })

        return result
    
    
    @mcp.tool()
    async def search_events(
        query: Annotated[str, "Search term. Case-insensitive substring search."],
        calendarName: Annotated[
            str | None,
            "Optional target calendar name. If omitted, all calendars are searched."
        ] = None,
    ) -> list[dict]:
        """Searches events by text in summary, description, or location."""

        getLogger().info(
            "Executing search_events for query='%s', calendar='%s'.",
            query,
            calendarName or "all",
        )

        if not query or not query.strip():
            raise ValueError("Search query must not be empty")

        client = get_client()
        calendars = client.principal().calendars()

        if not calendars:
            raise ValueError("No calendars available")

        # If a calendar name was specified, search only that calendar.
        if calendarName:
            calendars_to_search = [
                c for c in calendars
                if getattr(c, "name", None) == calendarName
            ]

            if not calendars_to_search:
                raise ValueError(f"Calendar '{calendarName}' not found")
        else:
            # No calendar specified -> search all calendars
            calendars_to_search = calendars

        search_term = query.strip().casefold()

        result = []

        for calendar in calendars_to_search:
            calendar_name = getattr(calendar, "name", "Unknown")

            getLogger().debug(
                "Searching calendar '%s'.",
                calendar_name,
            )

            # Fetch all events from the calendar
            events = calendar.events()

            for e in events:
                vevent = e.vobject_instance.vevent

                uid = get_vobject_value(vevent, "uid", "n/a")
                summary = get_vobject_value(vevent, "summary", "")
                description = get_vobject_value(vevent, "description", "")
                location = get_vobject_value(vevent, "location", "")

                # Search case-insensitively in all relevant fields
                searchable_text = " ".join([
                    summary,
                    description,
                    location,
                ]).casefold()

                if search_term not in searchable_text:
                    continue

                result.append({
                    "calendar": calendar_name,
                    "uid": uid,
                    "summary": summary or "No Title",
                    "description": description,
                    "location": location,
                    "start": str(
                        getattr(
                            getattr(vevent, "dtstart", None),
                            "value",
                            ""
                        )
                    ),
                    "end": str(
                        getattr(
                            getattr(vevent, "dtend", None),
                            "value",
                            ""
                        )
                    ),
                })

        getLogger().info(
            "Found %d events matching '%s'.",
            len(result),
            query,
        )

        return result
    
    
    @mcp.tool()
    async def get_next_event(
        from_datetime: Annotated[str, "Starting datetime (ISO 8601)"],
        calendarName: Annotated[
            str | None,
            "Optional target calendar name. If omitted, all calendars are searched."
        ] = None,
    ) -> dict | None:
        """Returns the next event starting after the given datetime."""

        getLogger().info(
            "Executing get_next_event from '%s', calendar='%s'.",
            from_datetime,
            calendarName or "all",
        )

        start = parse_dt(from_datetime)

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

        next_event = None
        next_event_start = None
        next_calendar_name = None

        for calendar in calendars_to_search:
            calendar_name = getattr(calendar, "name", "Unknown")

            # Search events from the requested datetime onwards
            events = calendar.date_search(
                start=start,
                end=start.replace(year=start.year + 1),
            )

            for event in events:
                vevent = event.vobject_instance.vevent

                dtstart = getattr(vevent, "dtstart", None)

                if dtstart is None:
                    continue

                event_start = dtstart.value

                # Convert date-only events to datetime
                if not isinstance(event_start, type(start)):
                    continue

                if event_start < start:
                    continue

                if next_event_start is None or event_start < next_event_start:
                    next_event = vevent
                    next_event_start = event_start
                    next_calendar_name = calendar_name

        if next_event is None:
            return None

        return {
            "calendar": next_calendar_name,
            "uid": get_vobject_value(next_event, "uid", "n/a"),
            "summary": get_vobject_value(next_event, "summary", "No Title"),
            "description": get_vobject_value(next_event, "description", ""),
            "location": get_vobject_value(next_event, "location", ""),
            "start": str(
                getattr(next_event.dtstart, "value", "")
            ),
            "end": str(
                getattr(
                    getattr(next_event, "dtend", None),
                    "value",
                    ""
                )
            ),
        }