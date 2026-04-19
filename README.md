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

The server exposes the service port 8123. The endpoint u want to query is
````http://caldav-server-adress:8123/mcp````
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