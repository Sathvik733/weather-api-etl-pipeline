"""Functions for retrieving weather data from Open-Meteo."""

from typing import Any

import requests

from src.config import OPEN_METEO_BASE_URL


def fetch_weather_data(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch hourly weather data for one location."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Asia/Kolkata",
        "forecast_days": 1,
    }

    response = requests.get(
        OPEN_METEO_BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()