"""Save transformed weather records to CSV."""

import csv
from pathlib import Path
from typing import Any

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger


CSV_FILE_NAME = "weather_hourly.csv"

CSV_FIELDNAMES = [
    "city_name",
    "weather_timestamp",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "source_system",
    "extracted_at_utc",
]


def save_to_csv(
    records: list[dict[str, Any]],
) -> Path:
    """Save transformed weather records to a CSV file."""

    if not records:
        raise ValueError(
            "Cannot save an empty list of records to CSV."
        )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_file_path = PROCESSED_DATA_DIR / CSV_FILE_NAME

    with csv_file_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDNAMES,
        )

        writer.writeheader()
        writer.writerows(records)

    logger.info(
        "Saved %s records to CSV",
        len(records),
    )

    return csv_file_path