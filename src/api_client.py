"""Fetch weather data from the Open-Meteo API."""

from typing import Any

import requests

from src.utils.config import (
    HOURLY_WEATHER_FIELDS,
    OPEN_METEO_BASE_URL,
)
from src.utils.logger import logger


def fetch_weather_data(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch hourly weather data for the supplied coordinates."""

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_WEATHER_FIELDS),
        "forecast_days": 1,
        "timezone": "UTC",
    }

    logger.info(
        "Requesting weather data for latitude=%s, longitude=%s",
        latitude,
        longitude,
    )

    try:
        response = requests.get(
            OPEN_METEO_BASE_URL,
            params=parameters,
            timeout=30,
        )

        response.raise_for_status()

        weather_data: dict[str, Any] = response.json()

        logger.info(
            "Weather API request completed successfully."
        )

        return weather_data

    except requests.Timeout:
        logger.exception(
            "Weather API request timed out."
        )
        raise

    except requests.RequestException:
        logger.exception(
            "Weather API request failed."
        )
        raise

    except ValueError:
        logger.exception(
            "Weather API returned invalid JSON."
        )
        raise