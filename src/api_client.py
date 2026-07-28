"""Retrieve hourly weather data from Open-Meteo."""

from typing import Any

import requests

from src.utils.config import (
    HOURLY_WEATHER_FIELDS,
    OPEN_METEO_BASE_URL,
)
from src.utils.logger import logger


class WeatherAPIError(Exception):
    """Raised when weather data cannot be retrieved."""


def fetch_weather_data(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch hourly weather data for one coordinate."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_WEATHER_FIELDS),
        "forecast_days": 1,
        "timezone": "auto",
    }

    logger.info(
        "Requesting weather data for latitude=%s, longitude=%s",
        latitude,
        longitude,
    )

    try:
        response = requests.get(
            OPEN_METEO_BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

    except requests.Timeout as error:
        raise WeatherAPIError(
            "Weather API request timed out."
        ) from error

    except requests.HTTPError as error:
        raise WeatherAPIError(
            f"Weather API returned an HTTP error: {error}"
        ) from error

    except requests.ConnectionError as error:
        raise WeatherAPIError(
            f"Weather API connection failed: {error}"
        ) from error

    except requests.RequestException as error:
        raise WeatherAPIError(
            f"Weather API request failed: {error}"
        ) from error

    try:
        response_data = response.json()

    except requests.JSONDecodeError as error:
        raise WeatherAPIError(
            "Weather API returned invalid JSON."
        ) from error

    if not isinstance(response_data, dict):
        raise WeatherAPIError(
            "Weather API returned an invalid response format."
        )

    logger.info(
        "Weather API request completed successfully."
    )

    return response_data