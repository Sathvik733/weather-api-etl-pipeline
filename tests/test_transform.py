"""Tests for weather-data transformation."""

import pytest

from src.transform import (
    WeatherTransformationError,
    transform_weather_data,
)


def test_transform_weather_data_success(
    valid_api_response,
) -> None:
    """Valid API data should produce clean hourly records."""

    records = transform_weather_data(
        city_name="Hyderabad",
        weather_data=valid_api_response,
    )

    assert len(records) == 2

    first_record = records[0]

    assert first_record["city_name"] == "Hyderabad"
    assert first_record["temperature_2m"] == 24.5
    assert first_record["relative_humidity_2m"] == 80
    assert first_record["precipitation"] == 0.0
    assert first_record["wind_speed_10m"] == 12.4
    assert first_record["source_system"] == "open_meteo"


def test_transform_weather_data_missing_hourly() -> None:
    """Missing hourly data should raise a transformation error."""

    with pytest.raises(
        WeatherTransformationError,
        match="Missing or invalid hourly data",
    ):
        transform_weather_data(
            city_name="Hyderabad",
            weather_data={},
        )


def test_transform_weather_data_array_length_mismatch(
    valid_api_response,
) -> None:
    """Different hourly-array lengths should raise an error."""

    valid_api_response["hourly"]["temperature_2m"] = [
        24.5
    ]

    with pytest.raises(
        WeatherTransformationError,
        match="different lengths",
    ):
        transform_weather_data(
            city_name="Hyderabad",
            weather_data=valid_api_response,
        )


def test_transform_weather_data_invalid_timestamp(
    valid_api_response,
) -> None:
    """Invalid timestamps should raise a transformation error."""

    valid_api_response["hourly"]["time"][0] = (
        "invalid-timestamp"
    )

    with pytest.raises(
        WeatherTransformationError,
        match="Invalid weather timestamp",
    ):
        transform_weather_data(
            city_name="Hyderabad",
            weather_data=valid_api_response,
        )