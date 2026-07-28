"""Transform raw Open-Meteo responses into clean hourly records."""

from datetime import datetime, timezone
from typing import Any


class WeatherTransformationError(Exception):
    """Raised when weather data cannot be transformed safely."""


def transform_weather_data(
    city_name: str,
    weather_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Convert nested hourly weather arrays into database-ready records."""

    hourly_data = weather_data.get("hourly")

    if not isinstance(hourly_data, dict):
        raise WeatherTransformationError(
            f"Missing or invalid hourly data for {city_name}."
        )

    timestamps = hourly_data.get("time", [])
    temperatures = hourly_data.get("temperature_2m", [])
    humidities = hourly_data.get(
        "relative_humidity_2m",
        [],
    )
    precipitation_values = hourly_data.get(
        "precipitation",
        [],
    )
    wind_speed_values = hourly_data.get(
        "wind_speed_10m",
        [],
    )

    hourly_arrays = {
        "timestamps": timestamps,
        "temperatures": temperatures,
        "humidities": humidities,
        "precipitation": precipitation_values,
        "wind_speed": wind_speed_values,
    }

    for field_name, field_values in hourly_arrays.items():
        if not isinstance(field_values, list):
            raise WeatherTransformationError(
                f"Invalid {field_name} data for {city_name}."
            )

    lengths = {
        len(timestamps),
        len(temperatures),
        len(humidities),
        len(precipitation_values),
        len(wind_speed_values),
    }

    if len(lengths) != 1:
        raise WeatherTransformationError(
            f"Hourly arrays have different lengths for {city_name}."
        )

    if not timestamps:
        raise WeatherTransformationError(
            f"No hourly records found for {city_name}."
        )

    extracted_at_utc = datetime.now(
        timezone.utc
    )

    transformed_records: list[dict[str, Any]] = []

    for (
        timestamp,
        temperature,
        humidity,
        precipitation,
        wind_speed,
    ) in zip(
        timestamps,
        temperatures,
        humidities,
        precipitation_values,
        wind_speed_values,
    ):
        try:
            weather_timestamp = datetime.fromisoformat(
                timestamp
            )
        except (TypeError, ValueError) as error:
            raise WeatherTransformationError(
                f"Invalid weather timestamp for {city_name}: "
                f"{timestamp}"
            ) from error

        record = {
            "city_name": city_name,
            "weather_timestamp": weather_timestamp,
            "temperature_2m": temperature,
            "relative_humidity_2m": humidity,
            "precipitation": precipitation,
            "wind_speed_10m": wind_speed,
            "source_system": "open_meteo",
            "extracted_at_utc": extracted_at_utc,
        }

        transformed_records.append(record)

    return transformed_records