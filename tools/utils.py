import logging
import sys
import os
import caldav
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("caldav-streamable-mcp")

CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASS = os.getenv("CALDAV_PASS")
MCP_SSL_VERIFY = os.getenv("MCP_SSL_VERIFY", "True").lower() == "true"

logger.info(f"CALDAV_URL: {CALDAV_URL}")
logger.info(f"CALDAV_USER: {CALDAV_USER}")

def get_client():
    if not all([CALDAV_URL, CALDAV_USER, CALDAV_PASS]):
        logger.error("Missing CALDAV env vars!")
        raise RuntimeError("Missing CALDAV env vars")

    return caldav.DAVClient(
        url=CALDAV_URL,
        username=CALDAV_USER,
        password=CALDAV_PASS,
        ssl_verify_cert=MCP_SSL_VERIFY
    )


def parse_dt(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str)

def getLogger():
    return logger