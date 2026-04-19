from .calendars import register_calendar_tools
from .events import register_event_tools


def register_tools(mcp):
    register_calendar_tools(mcp)
    register_event_tools(mcp)