# Power Outage Tracker

A Python script that monitors planned power outages from PGE Dystrybucja (Polish power distribution company) and sends alerts via Healthchecks.io when your street is scheduled for an outage.

## How It Works

1. Scrapes the PGE planned outages page using Playwright (headless Chromium)
2. Searches for a specific city and street for tomorrow's date
3. If the street is found in the outage list, triggers a Healthchecks.io failure alert
4. If not found, pings Healthchecks.io to confirm the check ran successfully

## Requirements

- Python 3.12+
- Docker (recommended) or local Playwright installation
- Healthchecks.io account (free tier available)

## Configuration

Configuration is loaded from a JSON file containing sensitive location data. This file must never be committed to the repository.

### Setup

```bash
cp secrets/config.json.example secrets/config.json
```

Edit `secrets/config.json` with your values:

```json
{
  "city": "Your_City",
  "destination": "Your_Street_Name_Only",
  "healthcheck_url": "Your_Healthchecks.io_URL",
  "interval_hours": 6
}
```

| Field | Description |
|-------|-------------|
| `city` | City name as it appears on the PGE website |
| `destination` | Street name (partial match supported) |
| `healthcheck_url` | Your Healthchecks.io ping URL |
| `interval_hours` | How often to check (0-24). Set to `0` for single run mode |

### Scheduling Behavior

The `interval_hours` setting controls how the container runs:

| Value | Behavior |
|-------|----------|
| `0` | Run once and exit |
| `1-24` | Run continuously, checking every N hours |

Values outside 0-24 are automatically clamped (e.g., `26` becomes `24`, `-5` becomes `0`).

For Portainer or standalone Docker without job scheduling, set `interval_hours` to a value like `6` to keep the container running and checking periodically.

## Running

### Docker Compose (Recommended)

```bash
docker compose up --build
```

### Docker with Manual Mount

```bash
docker build -t power-outage-tracker .
docker run --rm -v $(pwd)/secrets/config.json:/run/secrets/config.json:ro power-outage-tracker
```

### Local Development

Install dependencies:

```bash
pip install playwright requests
playwright install chromium
```

Run with environment variable:

```bash
CONFIG_JSON='{"city":"...","destination":"...","healthcheck_url":"..."}' python main.py
```

## Deployment

### Portainer / Standalone Docker

Since Docker Secrets require Swarm mode, use a bind mount on the host:

1. Create the config file on the host:
   ```bash
   sudo mkdir -p /opt/poweroutage
   sudo nano /opt/poweroutage/config.json
   sudo chmod 600 /opt/poweroutage/config.json
   ```

2. In Portainer, add a volume mount:
   - Host: `/opt/poweroutage/config.json`
   - Container: `/run/secrets/config.json`
   - Read-only: Yes

### Scheduling

Run daily via cron or a container scheduler. Example cron entry:

```
0 8 * * * docker run --rm -v /opt/poweroutage/config.json:/run/secrets/config.json:ro power-outage-tracker
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (street found or not found, healthcheck pinged) |
| 1 | Configuration error |
| 2 | Page timeout (website structure may have changed) |
| 3 | Unexpected error |

## Project Structure

```
PowerOutageTracker/
├── main.py                 # Main script
├── Dockerfile              # Container build file
├── docker-compose.yml      # Compose configuration
├── pyproject.toml          # Python dependencies
├── secrets/
│   ├── config.json         # Your config (gitignored)
│   └── config.json.example # Template
└── README.md
```

## Security

- Location data is stored outside the codebase in `secrets/config.json`
- The secrets directory is gitignored
- No default values expose user location
- The application fails immediately if configuration is missing

## License

See [LICENSE](LICENSE) file.
