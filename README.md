# CalDAV Streamable MCP Server

A lightweight MCP server for interacting with CalDAV calendars (e.g. Nextcloud, iCloud, Radicale).
It exposes tools for reading and writing calendar data via the MCP protocol.

---

## ✨ Features

* 📅 Read, create and delete calendars
* 📖 Read, create, delete and search events (single calendar or across all)
* 🌐 Streamable HTTP transport (`/mcp`)
* 🧩 Modular structure (`tools/`)

---

## ⚙️ Configuration

Configuration is done via environment variables:

```env
CALDAV_URL=https://your-caldav-server.com
CALDAV_USER=youruser
CALDAV_PASS=yourpassword
MCP_SSL_VERIFY=true
```

---

## 🐳 Docker Compose (recommended)

```yaml
version: "3.9"

services:
  caldav-mcp:
    image: dockersilas/caldav-streamable-mcp:latest
    container_name: caldav-mcp-server

    ports:
      - "8123:8123"

    env_file:
      - .env

    restart: unless-stopped
```

### Start

```bash
docker compose up -d
```

---

## 🚀 Run without Docker Compose

You can also start the container directly using `docker run`:

```bash
docker run -p 8123:8123 \
  --env-file .env \
  dockersilas/caldav-streamable-mcp:latest
```

---

## 🌐 Access

After startup, the MCP endpoint is available at:

```
http://localhost:8123/mcp
```

---

## 🧱 Project Structure

```text
.
├── server.py
├── tools/
│   ├── calendars.py
│   └── events/
│       ├── read.py
│       └── write.py
```

---

## 🛠 MCP Tools

The server provides the following tools for managing CalDAV calendars and events:

📅 Calendars
```text
list_calendars — Lists all available calendars.
create_calendar — Creates a new calendar with an optional description and color.
delete_calendar — Deletes a calendar by name.
```
📆 Events
```text
list_events_between — Lists events within a specified timeframe for one calendar.
list_all_events — Lists events across all calendars within a specified timeframe.
list_day_events — Lists all events for a specific day, optionally limited to one calendar.
search_events — Searches events by text in their summary, description, or location.
get_next_event — Returns the next event after a specified datetime.
create_event — Creates a new calendar event.
delete_event — Deletes an event by UID, optionally limited to one calendar.
```
🩺 Health
```text
GET /health — Returns the current health status of the server.
```

---

## 🛠️ Development

### Run locally

```bash
pip install -r requirements.txt
python server.py
```

---

## 🔐 Security Notes

* Never commit credentials to your repository
* Add `.env` to `.gitignore`
* Use HTTPS + reverse proxy for external access

---

## 📌 Notes

* Works with any CalDAV-compatible server
* Datetime format must be ISO-8601 (`YYYY-MM-DDTHH:MM:SS`)
* All-day events are automatically detected