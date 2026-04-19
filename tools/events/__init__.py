from .read import register_event_read_tools
from .write import register_event_write_tools


def register_event_tools(mcp):
    register_event_read_tools(mcp)
    register_event_write_tools(mcp)