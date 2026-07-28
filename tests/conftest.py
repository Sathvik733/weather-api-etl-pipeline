"""Shared pytest fixtures for the weather ETL test suite."""

from datetime import datetime, timezone
from typing import Any

import pytest


@pytest.fixture
def valid_api_response() -> dict[str, Any]:
    """Return a valid sample Open-Meteo API response."""

    return {
        "hourly": {
            "time": [
                "2026-07-28T00:00",
                "2026-07-28T01:00",
            ],
            "temperature_2m": [
                24.5,
                24.1,
            ],
            "relative_humidity_2m": [
                80,
                82,
            ],
            "precipitation": [
                0.0,
                0.2,
            ],
            "wind_speed_10m": [
                12.4,
                13.1,
            ],
        }
    }


@pytest.fixture
def valid_weather_record() -> dict[str, Any]:
    """Return one valid transformed weather record."""

    return {
        "city_name": "Hyderabad",
        "weather_timestamp": datetime(
            2026,
            7,
            28,
            0,
            0,
        ),
        "temperature_2m": 24.5,
        "relative_humidity_2m": 80,
        "precipitation": 0.0,
        "wind_speed_10m": 12.4,
        "source_system": "open_meteo",
        "extracted_at_utc": datetime.now(
            timezone.utc
        ),
    }