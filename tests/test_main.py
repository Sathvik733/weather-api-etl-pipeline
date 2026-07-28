"""Tests for the weather ETL pipeline orchestration."""

from pathlib import Path
from unittest.mock import MagicMock, call, patch

from src.main import run_pipeline


@patch("src.main.load_weather_records")
@patch("src.main.save_to_csv")
@patch("src.main.validate_weather_records")
@patch("src.main.transform_weather_data")
@patch("src.main.save_raw_record")
@patch("src.main.build_raw_record")
@patch("src.main.fetch_weather_data")
@patch("src.main.create_raw_data_directory")
def test_run_pipeline_success(
    mock_create_raw_directory: MagicMock,
    mock_fetch_weather_data: MagicMock,
    mock_build_raw_record: MagicMock,
    mock_save_raw_record: MagicMock,
    mock_transform_weather_data: MagicMock,
    mock_validate_weather_records: MagicMock,
    mock_save_to_csv: MagicMock,
    mock_load_weather_records: MagicMock,
    valid_api_response,
    valid_weather_record,
) -> None:
    """The complete pipeline should execute every ETL stage."""

    test_cities = [
        {
            "name": "Hyderabad",
            "latitude": 17.385,
            "longitude": 78.4867,
        },
        {
            "name": "Bengaluru",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
    ]

    hyderabad_record = valid_weather_record.copy()

    bengaluru_record = valid_weather_record.copy()
    bengaluru_record["city_name"] = "Bengaluru"

    mock_fetch_weather_data.return_value = (
        valid_api_response
    )

    mock_build_raw_record.return_value = {
        "source_system": "open_meteo",
        "response_payload": valid_api_response,
    }

    mock_save_raw_record.side_effect = [
        Path("hyderabad_test.json"),
        Path("bengaluru_test.json"),
    ]

    mock_transform_weather_data.side_effect = [
        [hyderabad_record],
        [bengaluru_record],
    ]

    validated_records = [
        hyderabad_record,
        bengaluru_record,
    ]

    mock_validate_weather_records.return_value = (
        validated_records
    )

    mock_save_to_csv.return_value = Path(
        "data/processed/weather_hourly.csv"
    )

    mock_load_weather_records.return_value = 2

    with patch(
        "src.main.CITIES",
        test_cities,
    ):
        run_pipeline()

    mock_create_raw_directory.assert_called_once()

    assert mock_fetch_weather_data.call_count == 2

    mock_fetch_weather_data.assert_has_calls(
        [
            call(
                latitude=17.385,
                longitude=78.4867,
            ),
            call(
                latitude=12.9716,
                longitude=77.5946,
            ),
        ]
    )

    assert mock_build_raw_record.call_count == 2
    assert mock_save_raw_record.call_count == 2
    assert mock_transform_weather_data.call_count == 2

    mock_validate_weather_records.assert_called_once_with(
        validated_records
    )

    mock_save_to_csv.assert_called_once_with(
        validated_records
    )

    mock_load_weather_records.assert_called_once_with(
        validated_records
    )


@patch("src.main.load_weather_records")
@patch("src.main.save_to_csv")
@patch("src.main.validate_weather_records")
@patch("src.main.transform_weather_data")
@patch("src.main.save_raw_record")
@patch("src.main.build_raw_record")
@patch("src.main.fetch_weather_data")
@patch("src.main.create_raw_data_directory")
def test_run_pipeline_with_no_transformed_records(
    mock_create_raw_directory: MagicMock,
    mock_fetch_weather_data: MagicMock,
    mock_build_raw_record: MagicMock,
    mock_save_raw_record: MagicMock,
    mock_transform_weather_data: MagicMock,
    mock_validate_weather_records: MagicMock,
    mock_save_to_csv: MagicMock,
    mock_load_weather_records: MagicMock,
    valid_api_response,
) -> None:
    """The pipeline should stop when transformation produces no records."""

    test_cities = [
        {
            "name": "Hyderabad",
            "latitude": 17.385,
            "longitude": 78.4867,
        }
    ]

    mock_fetch_weather_data.return_value = (
        valid_api_response
    )

    mock_build_raw_record.return_value = {
        "source_system": "open_meteo",
        "response_payload": valid_api_response,
    }

    mock_save_raw_record.return_value = Path(
        "hyderabad_test.json"
    )

    mock_transform_weather_data.return_value = []

    with patch(
        "src.main.CITIES",
        test_cities,
    ):
        run_pipeline()

    mock_validate_weather_records.assert_not_called()
    mock_save_to_csv.assert_not_called()
    mock_load_weather_records.assert_not_called()


@patch("src.main.load_weather_records")
@patch("src.main.save_to_csv")
@patch("src.main.validate_weather_records")
@patch("src.main.transform_weather_data")
@patch("src.main.save_raw_record")
@patch("src.main.build_raw_record")
@patch("src.main.fetch_weather_data")
@patch("src.main.create_raw_data_directory")
def test_run_pipeline_continues_after_city_failure(
    mock_create_raw_directory: MagicMock,
    mock_fetch_weather_data: MagicMock,
    mock_build_raw_record: MagicMock,
    mock_save_raw_record: MagicMock,
    mock_transform_weather_data: MagicMock,
    mock_validate_weather_records: MagicMock,
    mock_save_to_csv: MagicMock,
    mock_load_weather_records: MagicMock,
    valid_api_response,
    valid_weather_record,
) -> None:
    """Failure for one city should not stop other cities."""

    test_cities = [
        {
            "name": "Hyderabad",
            "latitude": 17.385,
            "longitude": 78.4867,
        },
        {
            "name": "Bengaluru",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
    ]

    mock_fetch_weather_data.side_effect = [
        RuntimeError("Temporary API failure"),
        valid_api_response,
    ]

    mock_build_raw_record.return_value = {
        "source_system": "open_meteo",
        "response_payload": valid_api_response,
    }

    mock_save_raw_record.return_value = Path(
        "bengaluru_test.json"
    )

    bengaluru_record = valid_weather_record.copy()
    bengaluru_record["city_name"] = "Bengaluru"

    mock_transform_weather_data.return_value = [
        bengaluru_record
    ]

    mock_validate_weather_records.return_value = [
        bengaluru_record
    ]

    mock_save_to_csv.return_value = Path(
        "data/processed/weather_hourly.csv"
    )

    mock_load_weather_records.return_value = 1

    with patch(
        "src.main.CITIES",
        test_cities,
    ):
        run_pipeline()

    assert mock_fetch_weather_data.call_count == 2

    mock_transform_weather_data.assert_called_once_with(
        city_name="Bengaluru",
        weather_data=valid_api_response,
    )

    mock_validate_weather_records.assert_called_once_with(
        [bengaluru_record]
    )

    mock_load_weather_records.assert_called_once_with(
        [bengaluru_record]
    )


@patch("src.main.load_weather_records")
@patch("src.main.save_to_csv")
@patch("src.main.validate_weather_records")
@patch("src.main.transform_weather_data")
@patch("src.main.save_raw_record")
@patch("src.main.build_raw_record")
@patch("src.main.fetch_weather_data")
@patch("src.main.create_raw_data_directory")
def test_run_pipeline_stops_when_validation_fails(
    mock_create_raw_directory: MagicMock,
    mock_fetch_weather_data: MagicMock,
    mock_build_raw_record: MagicMock,
    mock_save_raw_record: MagicMock,
    mock_transform_weather_data: MagicMock,
    mock_validate_weather_records: MagicMock,
    mock_save_to_csv: MagicMock,
    mock_load_weather_records: MagicMock,
    valid_api_response,
    valid_weather_record,
) -> None:
    """CSV and database stages should not run after validation failure."""

    test_cities = [
        {
            "name": "Hyderabad",
            "latitude": 17.385,
            "longitude": 78.4867,
        }
    ]

    mock_fetch_weather_data.return_value = (
        valid_api_response
    )

    mock_build_raw_record.return_value = {
        "source_system": "open_meteo",
        "response_payload": valid_api_response,
    }

    mock_save_raw_record.return_value = Path(
        "hyderabad_test.json"
    )

    mock_transform_weather_data.return_value = [
        valid_weather_record
    ]

    mock_validate_weather_records.side_effect = (
        ValueError("Validation failed")
    )

    with patch(
        "src.main.CITIES",
        test_cities,
    ):
        run_pipeline()

    mock_validate_weather_records.assert_called_once_with(
        [valid_weather_record]
    )

    mock_save_to_csv.assert_not_called()
    mock_load_weather_records.assert_not_called()