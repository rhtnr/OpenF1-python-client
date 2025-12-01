# 🏎️ OpenF1 Python Client

A production-grade Python SDK for the [OpenF1 API](https://openf1.org/), providing easy access to real-time and historical Formula 1 data.

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://pydantic.dev"><img src="https://img.shields.io/badge/pydantic-v2-E92063.svg" alt="Pydantic v2"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</p>

<p align="center">
  <a href="https://buymeacoffee.com/rhtnr"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Filtering Data](#-filtering-data)
- [Available Endpoints](#-available-endpoints)
- [Endpoint Methods](#️-endpoint-methods)
- [Configuration](#️-configuration)
- [Error Handling](#️-error-handling)
- [Logging](#-logging)
- [Data Models](#-data-models)
- [Examples](#-examples)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Features

- 🔌 **Full API Coverage** — Access all 16 OpenF1 endpoints including telemetry, lap times, positions, weather, and more
- 🔒 **Type Safety** — Fully typed with Pydantic v2 models and comprehensive type hints
- 🎯 **Pythonic Filtering** — Use dictionaries with comparison operators for flexible queries
- 🔐 **Authentication Support** — OAuth2 password flow for real-time data access
- ⚠️ **Robust Error Handling** — Comprehensive exception hierarchy with detailed error information
- 🚀 **Production Ready** — Automatic retries, configurable timeouts, and logging support
- 📊 **Multiple Formats** — JSON and CSV response support

---

## 📦 Installation

```bash
pip install openf1-client
```

Or install from source:

```bash
git clone https://github.com/YOUR_USERNAME/openf1-python.git
cd openf1-python
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

---

## 🚀 Quick Start

### Basic Usage (Unauthenticated)

Historical data is available without authentication:

```python
from openf1_client import OpenF1Client

# Create a client
client = OpenF1Client()

# Get lap data for a specific driver
laps = client.laps.list(
    session_key=9161,
    driver_number=63,
)

for lap in laps:
    print(f"Lap {lap.lap_number}: {lap.lap_duration}s")

# Don't forget to close the client when done
client.close()
```

### Using Context Manager

```python
from openf1_client import OpenF1Client

with OpenF1Client() as client:
    # Get driver information
    drivers = client.drivers.list(session_key=9158)

    for driver in drivers:
        print(f"{driver.name_acronym}: {driver.full_name} - {driver.team_name}")
```

### 🔐 Authenticated Usage

For real-time data and higher rate limits, authenticate with your OpenF1 credentials:

```python
from openf1_client import OpenF1Client

client = OpenF1Client(
    username="your_email@example.com",
    password="your_password",
)

# Access real-time data
latest_session = client.sessions.first(session_key="latest")
print(f"Current session: {latest_session.session_name}")
```

Or use a pre-existing access token:

```python
client = OpenF1Client(access_token="your_access_token")
```

---

## 🔍 Filtering Data

OpenF1 supports rich filtering with comparison operators. The client provides a Pythonic interface:

### Simple Equality

```python
# Filter by exact values
laps = client.laps.list(
    session_key=9161,
    driver_number=63,
    lap_number=8,
)
```

### Comparison Operators

Use dictionaries with operator keys for comparisons:

```python
# Speed >= 315 km/h
fast_telemetry = client.car_data.list(
    session_key=9159,
    driver_number=55,
    speed={">=": 315},
)

# Close intervals (< 0.5 seconds)
close_battles = client.intervals.list(
    session_key=9161,
    interval={"<": 0.5},
)
```

### Range Filters

```python
# Date range
location_data = client.location.list(
    session_key=9161,
    driver_number=81,
    date={
        ">": "2023-09-16T13:03:35.200",
        "<": "2023-09-16T13:03:35.800",
    },
)

# Lap range
stint_laps = client.laps.list(
    session_key=9161,
    driver_number=1,
    lap_number={">=": 10, "<=": 20},
)
```

### Using FilterBuilder

For more complex filters, use the `FilterBuilder` helper:

```python
from openf1_client import OpenF1Client, FilterBuilder

with OpenF1Client() as client:
    filters = (
        FilterBuilder()
        .eq("session_key", 9161)
        .eq("driver_number", 1)
        .gte("speed", 300)
        .lt("lap_number", 10)
        .build()
    )

    car_data = client.car_data.list(**filters)
```

---

## 📡 Available Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| 🏎️ `car_data` | Car telemetry (~3.7 Hz) | `client.car_data.list(...)` |
| 👤 `drivers` | Driver information | `client.drivers.list(...)` |
| ⏱️ `intervals` | Gap data (~4s updates) | `client.intervals.list(...)` |
| 🔄 `laps` | Lap timing data | `client.laps.list(...)` |
| 📍 `location` | Car positions (~3.7 Hz) | `client.location.list(...)` |
| 🏁 `meetings` | Grand Prix metadata | `client.meetings.list(...)` |
| 🔀 `overtakes` | Passing events (beta) | `client.overtakes.list(...)` |
| 🛞 `pit` | Pit stop activity | `client.pit.list(...)` |
| 📊 `position` | Track positions | `client.position.list(...)` |
| 🚩 `race_control` | Flags, incidents | `client.race_control.list(...)` |
| 📅 `sessions` | Session data | `client.sessions.list(...)` |
| 🏆 `session_result` | Final results (beta) | `client.session_result.list(...)` |
| 🚦 `starting_grid` | Grid positions (beta) | `client.starting_grid.list(...)` |
| 🔧 `stints` | Stint/tyre data | `client.stints.list(...)` |
| 📻 `team_radio` | Radio communications | `client.team_radio.list(...)` |
| 🌤️ `weather` | Weather data (~1 min) | `client.weather.list(...)` |

---

## 🛠️ Endpoint Methods

Each endpoint provides several methods:

```python
# List all matching records
laps = client.laps.list(session_key=9161, driver_number=1)

# Get first matching record (or None)
lap = client.laps.first(session_key=9161, driver_number=1, lap_number=1)

# Get raw data (dict) without model parsing
raw_data = client.laps.list_raw(session_key=9161)

# Get CSV format
csv_data = client.laps.list_csv(session_key=9161)

# Count matching records
count = client.laps.count(session_key=9161, driver_number=1)
```

Many endpoints also provide convenience methods:

```python
# 🔄 Laps
fastest_lap = client.laps.get_fastest_lap(session_key=9161)
flying_laps = client.laps.get_flying_laps(session_key=9161, driver_number=1)

# 📅 Sessions
races = client.sessions.get_races(year=2023)
latest = client.sessions.get_latest()

# 🔧 Stints
strategy = client.stints.get_tyre_strategy(session_key=9161, driver_number=1)

# 🌤️ Weather
rain = client.weather.get_rain_periods(session_key=9161)
```

---

## ⚙️ Configuration

```python
from openf1_client import OpenF1Client

client = OpenF1Client(
    # 🔐 Authentication
    username="user@example.com",
    password="secret",
    # Or use a token directly
    # access_token="your_token",

    # 🌐 Connection settings
    timeout=60.0,                    # Request timeout in seconds
    # timeout=(5.0, 30.0),           # (connect, read) timeouts
    max_retries=5,                   # Retry failed requests

    # 📄 Response format
    default_format="json",           # "json" or "csv"

    # 🔒 SSL/TLS
    verify_ssl=True,
)
```

---

## ⚠️ Error Handling

The client provides a comprehensive exception hierarchy:

```python
from openf1_client import (
    OpenF1Client,
    OpenF1Error,           # Base exception
    OpenF1ConfigError,     # Invalid configuration
    OpenF1TransportError,  # Network errors
    OpenF1APIError,        # API errors (non-2xx)
    OpenF1AuthError,       # 401/403 errors
    OpenF1RateLimitError,  # 429 errors
    OpenF1NotFoundError,   # 404 errors
    OpenF1ServerError,     # 5xx errors
    OpenF1TimeoutError,    # Request timeout
    OpenF1ValidationError, # Data validation
)

try:
    with OpenF1Client() as client:
        laps = client.laps.list(session_key=99999)
except OpenF1NotFoundError as e:
    print(f"❌ Session not found: {e}")
except OpenF1RateLimitError as e:
    print(f"⏳ Rate limited. Retry after: {e.retry_after}s")
except OpenF1APIError as e:
    print(f"⚠️ API error {e.status_code}: {e.message}")
except OpenF1Error as e:
    print(f"💥 Client error: {e}")
```

---

## 📝 Logging

Enable debug logging to see HTTP requests and responses:

```python
from openf1_client import setup_logging
import logging

# Enable debug logging
setup_logging(logging.DEBUG)

# Or configure manually
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openf1_client")
logger.setLevel(logging.DEBUG)
```

---

## 📊 Data Models

All responses are parsed into Pydantic models with full type annotations:

```python
from openf1_client import OpenF1Client, Lap, Driver

with OpenF1Client() as client:
    lap: Lap = client.laps.first(session_key=9161, driver_number=1, lap_number=1)

    if lap:
        print(f"Lap duration: {lap.lap_duration}")
        print(f"Sector 1: {lap.duration_sector_1}")
        print(f"Sector 2: {lap.duration_sector_2}")
        print(f"Sector 3: {lap.duration_sector_3}")
        print(f"Speed trap: {lap.st_speed} km/h")
```

---

## 💡 Examples

### 🏁 Analyze a Race

```python
from openf1_client import OpenF1Client

with OpenF1Client() as client:
    # Get session info
    session = client.sessions.first(session_key=9161)
    print(f"🏁 Session: {session.session_name} - {session.country_name}")

    # Get all drivers
    drivers = client.drivers.list(session_key=9161)

    for driver in drivers:
        # Get their fastest lap
        fastest = client.laps.get_fastest_lap(
            session_key=9161,
            driver_number=driver.driver_number,
        )

        # Get pit stops
        pit_count = client.pit.count_pit_stops(
            session_key=9161,
            driver_number=driver.driver_number,
        )

        # Get tyre strategy
        strategy = client.stints.get_tyre_strategy(
            session_key=9161,
            driver_number=driver.driver_number,
        )

        print(f"🏎️ {driver.name_acronym}: "
              f"Fastest: {fastest.lap_duration if fastest else 'N/A'}s, "
              f"Stops: {pit_count}, "
              f"Tyres: {' → '.join(strategy)}")
```

### 🌤️ Track Weather Changes

```python
from openf1_client import OpenF1Client

with OpenF1Client() as client:
    weather_data = client.weather.list(session_key=9161)

    for w in weather_data:
        rain_emoji = "🌧️" if w.rainfall else "☀️"
        print(f"{rain_emoji} {w.date}")
        print(f"   🌡️ Air: {w.air_temperature}°C")
        print(f"   🛣️ Track: {w.track_temperature}°C")
        print(f"   💧 Humidity: {w.humidity}%")
```

### 🔀 Find Overtakes

```python
from openf1_client import OpenF1Client
from collections import Counter

with OpenF1Client() as client:
    overtakes = client.overtakes.list(session_key=9161)

    print(f"🔀 Total overtakes: {len(overtakes)}")

    # Get drivers with most overtakes
    overtake_counts = Counter(o.driver_number for o in overtakes)

    print("\n🏆 Top overtakers:")
    for driver_num, count in overtake_counts.most_common(5):
        driver = client.drivers.first(
            session_key=9161,
            driver_number=driver_num,
        )
        print(f"   {driver.name_acronym}: {count} overtakes")
```

---

## 🔮 Future Enhancements

The client is designed to be easily extended. Planned additions:

### ⚡ Async Support

```python
# Future async client (design ready, not yet implemented)
from openf1_client import AsyncOpenF1Client

async with AsyncOpenF1Client() as client:
    laps = await client.laps.list(session_key=9161)
```

### 📡 Real-time Streaming

```python
# Future streaming support (design ready)
# Via MQTT or WebSockets for live data
async for telemetry in client.car_data.stream(driver_number=1):
    print(f"🏎️ Speed: {telemetry.speed} km/h")
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/openf1_client

# Format code
black src tests

# Lint code
ruff check src tests
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- 🏎️ [OpenF1](https://openf1.org/) for providing the excellent Formula 1 data API
- ❤️ The Formula 1 community for their passion and support

---

<p align="center">
  <strong>If you find this project useful, consider supporting its development:</strong>
</p>

<p align="center">
  <a href="https://buymeacoffee.com/rhtnr">
    <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee">
  </a>
</p>

<p align="center">
  Made with ❤️ for the F1 community
</p>
