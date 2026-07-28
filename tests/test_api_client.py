"""Tests for the Open-Meteo API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.api_client import (
    WeatherAPIError,
    fetch_weather_data,
)


@patch("src.api_client.requests.get")
def test_fetch_weather_data_success(
    mock_get: Mock,
) -> None:
    """A successful response should return parsed JSON."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2026-07-28T00:00"],
            "temperature_2m": [24.5],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
            "wind_speed_10m": [12.4],
        }
    }

    mock_get.return_value = mock_response

    result = fetch_weather_data(
        latitude=17.385,
        longitude=78.4867,
    )

    assert "hourly" in result
    assert result["hourly"]["temperature_2m"] == [24.5]

    mock_get.assert_called_once()


@patch("src.api_client.requests.get")
def test_fetch_weather_data_uses_expected_parameters(
    mock_get: Mock,
) -> None:
    """The request should include coordinates and weather fields."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "hourly": {}
    }

    mock_get.return_value = mock_response

    fetch_weather_data(
        latitude=17.385,
        longitude=78.4867,
    )

    _, call_kwargs = mock_get.call_args

    assert call_kwargs["params"]["latitude"] == 17.385
    assert call_kwargs["params"]["longitude"] == 78.4867
    assert "temperature_2m" in call_kwargs["params"]["hourly"]
    assert "relative_humidity_2m" in call_kwargs["params"]["hourly"]
    assert "precipitation" in call_kwargs["params"]["hourly"]
    assert "wind_speed_10m" in call_kwargs["params"]["hourly"]


@patch("src.api_client.requests.get")
def test_fetch_weather_data_timeout(
    mock_get: Mock,
) -> None:
    """A request timeout should raise WeatherAPIError."""

    mock_get.side_effect = requests.Timeout(
        "API request timed out"
    )

    with pytest.raises(
        WeatherAPIError,
        match="timed out",
    ):
        fetch_weather_data(
            latitude=17.385,
            longitude=78.4867,
        )


@patch("src.api_client.requests.get")
def test_fetch_weather_data_http_error(
    mock_get: Mock,
) -> None:
    """An HTTP failure should raise WeatherAPIError."""

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("500 Server Error")
    )

    mock_get.return_value = mock_response

    with pytest.raises(
        WeatherAPIError,
        match="HTTP error",
    ):
        fetch_weather_data(
            latitude=17.385,
            longitude=78.4867,
        )


@patch("src.api_client.requests.get")
def test_fetch_weather_data_connection_error(
    mock_get: Mock,
) -> None:
    """A network connection failure should raise WeatherAPIError."""

    mock_get.side_effect = requests.ConnectionError(
        "Connection failed"
    )

    with pytest.raises(
        WeatherAPIError,
        match="connection",
    ):
        fetch_weather_data(
            latitude=17.385,
            longitude=78.4867,
        )


@patch("src.api_client.requests.get")
def test_fetch_weather_data_invalid_json(
    mock_get: Mock,
) -> None:
    """Invalid JSON should raise WeatherAPIError."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = requests.JSONDecodeError(
        "Invalid JSON",
        "",
        0,
    )

    mock_get.return_value = mock_response

    with pytest.raises(
        WeatherAPIError,
        match="JSON",
    ):
        fetch_weather_data(
            latitude=17.385,
            longitude=78.4867,
        )


@patch("src.api_client.requests.get")
def test_fetch_weather_data_non_dictionary_response(
    mock_get: Mock,
) -> None:
    """A non-dictionary API response should be rejected."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        "unexpected",
        "response",
    ]

    mock_get.return_value = mock_response

    with pytest.raises(
        WeatherAPIError,
        match="invalid response",
    ):
        fetch_weather_data(
            latitude=17.385,
            longitude=78.4867,
        )