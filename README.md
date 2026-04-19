# CalDAV Streamable MCP Server

A lightweight MCP server for interacting with CalDAV calendars (e.g. Nextcloud, iCloud, Radicale).
It exposes tools for reading and writing calendar data via the MCP protocol.

---

## ✨ Features

* 📅 List calendars
* 📖 Read events (single calendar or across all)
* ✍️ Create events
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

🛠 MCP Tools (Short Overview)
list_calendars

Returns all available calendars.
````
Input: –
Output: { name, url }[]
````

list_events

Lists events for a specific calendar within a time range.
````
Input:
start (ISO 8601)
end (ISO 8601)
calendarUrl (string)

Output: { uid, summary, start, end }[]
````

list_all_events

Lists events across all calendars within a time range.
````
Input:
start (ISO 8601)
end (ISO 8601)

Output: { calendar, calendarUrl, uid, summary, start, end, allDay }[] (or error object)
````

create_event

Creates a new calendar event.
````
Input:
summary (string)
start (ISO 8601)
end (ISO 8601)
calendarUrl (optional)

Output: eventUrl (string)
````

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