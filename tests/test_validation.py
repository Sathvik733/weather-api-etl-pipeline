"""Tests for transformed weather-record validation."""

import pytest

from src.validation import (
    WeatherValidationError,
    validate_weather_record,
    validate_weather_records,
)


def test_validate_weather_record_success(
    valid_weather_record,
) -> None:
    """A valid weather record should pass validation."""

    validate_weather_record(
        valid_weather_record
    )


def test_validate_weather_record_missing_field(
    valid_weather_record,
) -> None:
    """A missing required field should fail validation."""

    del valid_weather_record["temperature_2m"]

    with pytest.raises(
        WeatherValidationError,
        match="Missing required fields",
    ):
        validate_weather_record(
            valid_weather_record
        )


def test_validate_weather_record_invalid_humidity(
    valid_weather_record,
) -> None:
    """Humidity above 100 should fail validation."""

    valid_weather_record[
        "relative_humidity_2m"
    ] = 150

    with pytest.raises(
        WeatherValidationError,
        match="between 0 and 100",
    ):
        validate_weather_record(
            valid_weather_record
        )


def test_validate_weather_record_negative_precipitation(
    valid_weather_record,
) -> None:
    """Negative precipitation should fail validation."""

    valid_weather_record["precipitation"] = -1.0

    with pytest.raises(
        WeatherValidationError,
        match="cannot be negative",
    ):
        validate_weather_record(
            valid_weather_record
        )


def test_validate_weather_record_negative_wind_speed(
    valid_weather_record,
) -> None:
    """Negative wind speed should fail validation."""

    valid_weather_record["wind_speed_10m"] = -5.0

    with pytest.raises(
        WeatherValidationError,
        match="cannot be negative",
    ):
        validate_weather_record(
            valid_weather_record
        )


def test_validate_weather_records_filters_invalid_record(
    valid_weather_record,
) -> None:
    """Bulk validation should remove invalid records."""

    invalid_record = valid_weather_record.copy()

    invalid_record[
        "relative_humidity_2m"
    ] = 150

    records = [
        valid_weather_record,
        invalid_record,
    ]

    valid_records = validate_weather_records(
        records
    )

    assert len(valid_records) == 1
    assert valid_records[0]["city_name"] == (
        "Hyderabad"
    )


def test_validate_weather_records_all_invalid(
    valid_weather_record,
) -> None:
    """Bulk validation should fail when all records are invalid."""

    valid_weather_record[
        "relative_humidity_2m"
    ] = 150

    with pytest.raises(
        WeatherValidationError,
        match="No valid weather records",
    ):
        validate_weather_records(
            [valid_weather_record]
        )