"""Validate transformed weather records before loading them."""

from datetime import datetime
from typing import Any

from src.utils.logger import logger


REQUIRED_FIELDS = {
    "city_name",
    "weather_timestamp",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "source_system",
    "extracted_at_utc",
}


class WeatherValidationError(Exception):
    """Raised when a weather record fails validation."""


def validate_weather_record(
    record: dict[str, Any],
) -> None:
    """Validate one transformed weather record."""

    missing_fields = REQUIRED_FIELDS - record.keys()

    if missing_fields:
        raise WeatherValidationError(
            f"Missing required fields: {sorted(missing_fields)}"
        )

    city_name = record["city_name"]

    if not isinstance(city_name, str) or not city_name.strip():
        raise WeatherValidationError(
            "city_name must be a non-empty string."
        )

    weather_timestamp = record["weather_timestamp"]

    if not isinstance(weather_timestamp, datetime):
        raise WeatherValidationError(
            "weather_timestamp must be a datetime object."
        )

    temperature = record["temperature_2m"]

    if not isinstance(temperature, (int, float)):
        raise WeatherValidationError(
            "temperature_2m must be numeric."
        )

    if not -100 <= temperature <= 70:
        raise WeatherValidationError(
            f"temperature_2m is outside the expected range: "
            f"{temperature}"
        )

    humidity = record["relative_humidity_2m"]

    if not isinstance(humidity, (int, float)):
        raise WeatherValidationError(
            "relative_humidity_2m must be numeric."
        )

    if not 0 <= humidity <= 100:
        raise WeatherValidationError(
            f"relative_humidity_2m must be between 0 and 100: "
            f"{humidity}"
        )

    precipitation = record["precipitation"]

    if not isinstance(precipitation, (int, float)):
        raise WeatherValidationError(
            "precipitation must be numeric."
        )

    if precipitation < 0:
        raise WeatherValidationError(
            f"precipitation cannot be negative: "
            f"{precipitation}"
        )

    wind_speed = record["wind_speed_10m"]

    if not isinstance(wind_speed, (int, float)):
        raise WeatherValidationError(
            "wind_speed_10m must be numeric."
        )

    if wind_speed < 0:
        raise WeatherValidationError(
            f"wind_speed_10m cannot be negative: "
            f"{wind_speed}"
        )

    source_system = record["source_system"]

    if source_system != "open_meteo":
        raise WeatherValidationError(
            f"Unexpected source system: {source_system}"
        )

    extracted_at_utc = record["extracted_at_utc"]

    if not isinstance(extracted_at_utc, datetime):
        raise WeatherValidationError(
            "extracted_at_utc must be a datetime object."
        )


def validate_weather_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate records and return only valid records."""

    valid_records: list[dict[str, Any]] = []
    invalid_count = 0

    for index, record in enumerate(records):
        try:
            validate_weather_record(record)
            valid_records.append(record)

        except WeatherValidationError as error:
            invalid_count += 1

            logger.warning(
                "Rejected weather record at index %s: %s | Record: %s",
                index,
                error,
                record,
            )

    logger.info(
        "Validation completed: %s valid, %s invalid",
        len(valid_records),
        invalid_count,
    )

    if not valid_records:
        raise WeatherValidationError(
            "No valid weather records remain after validation."
        )

    return valid_records