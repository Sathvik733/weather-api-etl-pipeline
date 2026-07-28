"""Tests for writing transformed weather records to CSV."""

import csv
from pathlib import Path

import pytest

from src.csv_writer import (
    CSV_FIELDNAMES,
    CSV_FILE_NAME,
    save_to_csv,
)


def test_save_to_csv_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    valid_weather_record,
) -> None:
    """Valid records should be written to a CSV file."""

    monkeypatch.setattr(
        "src.csv_writer.PROCESSED_DATA_DIR",
        tmp_path,
    )

    csv_file_path = save_to_csv(
        [valid_weather_record]
    )

    assert csv_file_path.exists()
    assert csv_file_path.is_file()
    assert csv_file_path.name == CSV_FILE_NAME

    with csv_file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert reader.fieldnames == CSV_FIELDNAMES
    assert len(rows) == 1

    first_row = rows[0]

    assert first_row["city_name"] == "Hyderabad"
    assert first_row["temperature_2m"] == "24.5"
    assert first_row["relative_humidity_2m"] == "80"
    assert first_row["precipitation"] == "0.0"
    assert first_row["wind_speed_10m"] == "12.4"
    assert first_row["source_system"] == "open_meteo"


def test_save_to_csv_multiple_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    valid_weather_record,
) -> None:
    """Multiple records should be written to the same CSV file."""

    monkeypatch.setattr(
        "src.csv_writer.PROCESSED_DATA_DIR",
        tmp_path,
    )

    second_record = valid_weather_record.copy()
    second_record["city_name"] = "Bengaluru"
    second_record["temperature_2m"] = 21.7

    csv_file_path = save_to_csv(
        [
            valid_weather_record,
            second_record,
        ]
    )

    with csv_file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["city_name"] == "Hyderabad"
    assert rows[1]["city_name"] == "Bengaluru"
    assert rows[1]["temperature_2m"] == "21.7"


def test_save_to_csv_creates_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    valid_weather_record,
) -> None:
    """The processed-data directory should be created automatically."""

    processed_directory = (
        tmp_path
        / "new_directory"
        / "processed"
    )

    monkeypatch.setattr(
        "src.csv_writer.PROCESSED_DATA_DIR",
        processed_directory,
    )

    assert not processed_directory.exists()

    csv_file_path = save_to_csv(
        [valid_weather_record]
    )

    assert processed_directory.exists()
    assert csv_file_path.exists()


def test_save_to_csv_empty_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty list should not create a CSV file."""

    monkeypatch.setattr(
        "src.csv_writer.PROCESSED_DATA_DIR",
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="empty list",
    ):
        save_to_csv([])


def test_save_to_csv_overwrites_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    valid_weather_record,
) -> None:
    """A new pipeline run should replace the previous CSV output."""

    monkeypatch.setattr(
        "src.csv_writer.PROCESSED_DATA_DIR",
        tmp_path,
    )

    first_file = save_to_csv(
        [valid_weather_record]
    )

    second_record = valid_weather_record.copy()
    second_record["city_name"] = "Bengaluru"

    second_file = save_to_csv(
        [second_record]
    )

    assert first_file == second_file

    with second_file.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(
            csv.DictReader(csv_file)
        )

    assert len(rows) == 1
    assert rows[0]["city_name"] == "Bengaluru"