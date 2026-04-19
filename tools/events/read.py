from mcp.server.fastmcp import FastMCP
from datetime import timezone

from ..utils import get_client, parse_dt


def register_event_read_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_events(start: str, end: str, calendarUrl: str):
        """Lists events within timeframe for one calendar."""
        client = get_client()
        calendar = client.calendar(url=calendarUrl)

        events = calendar.date_search(
            start=parse_dt(start),
            end=parse_dt(end)
        )

        result = []
        for e in events:
            vevent = e.vobject_instance.vevent

            result.append({
                "uid": str(getattr(vevent, "uid", "n/a")),
                "summary": str(getattr(vevent, "summary", "No Title")),
                "start": str(getattr(vevent.dtstart, "value", "")),
                "end": str(getattr(vevent.dtend, "value", "")),
            })

        return result


    @mcp.tool()
    async def list_all_events(start: str, end: str):
        """Lists events across all calendars."""
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
                        "uid": str(getattr(vevent, "uid", "n/a")),
                        "summary": str(getattr(vevent, "summary", "No Title")),
                        "start": str(safe_get(vevent, "dtstart")),
                        "end": str(safe_get(vevent, "dtend")),
                        "allDay": safe_get(vevent, "dtend") is None
                    })

            except Exception as err:
                result.append({
                    "calendar": str(calendar.name),
                    "error": str(err)
                })

        return result