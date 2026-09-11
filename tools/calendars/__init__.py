from .read import register_calendar_read_tools
from .write import register_calendar_write_tools


def register_calendar_tools(mcp):
    register_calendar_read_tools(mcp)
    register_calendar_write_tools(mcp)