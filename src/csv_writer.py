"""Save transformed weather records to CSV."""

import csv
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
CSV_FILE_PATH = PROCESSED_DATA_DIR / "weather_hourly.csv"


def create_processed_directory() -> None:
    """Create the processed-data directory if it does not exist."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_to_csv(
    records: list[dict[str, Any]],
) -> Path:
    """Save transformed weather records to a CSV file."""

    create_processed_directory()

    if not records:
        raise ValueError("Cannot save an empty list of weather records.")

    fieldnames = [
        "city_name",
        "weather_timestamp",
        "temperature_celsius",
        "relative_humidity_percent",
        "precipitation_mm",
    ]

    with CSV_FILE_PATH.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(records)

    return CSV_FILE_PATH