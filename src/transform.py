"""Transform raw Open-Meteo responses into clean hourly records."""

from datetime import datetime
from typing import Any


class WeatherTransformationError(Exception):
    """Raised when weather data cannot be transformed safely."""


def transform_weather_data(
    city_name: str,
    weather_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Convert nested hourly weather arrays into individual records."""

    hourly_data = weather_data.get("hourly")

    if not isinstance(hourly_data, dict):
        raise WeatherTransformationError(
            f"Missing or invalid hourly data for {city_name}."
        )

    timestamps = hourly_data.get("time", [])
    temperatures = hourly_data.get("temperature_2m", [])
    humidities = hourly_data.get("relative_humidity_2m", [])
    precipitation_values = hourly_data.get("precipitation", [])

    lengths = {
        len(timestamps),
        len(temperatures),
        len(humidities),
        len(precipitation_values),
    }

    if len(lengths) != 1:
        raise WeatherTransformationError(
            f"Hourly arrays have different lengths for {city_name}."
        )

    transformed_records: list[dict[str, Any]] = []

    for timestamp, temperature, humidity, precipitation in zip(
        timestamps,
        temperatures,
        humidities,
        precipitation_values,
    ):
        record = {
            "city_name": city_name,
            "weather_timestamp": datetime.fromisoformat(timestamp),
            "temperature_celsius": temperature,
            "relative_humidity_percent": humidity,
            "precipitation_mm": precipitation,
        }

        transformed_records.append(record)

    return transformed_records