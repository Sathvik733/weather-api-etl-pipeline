"""Run the weather ETL pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.api_client import fetch_weather_data
from src.config import CITIES
from src.csv_writer import save_to_csv
from src.database import load_weather_records
from src.transform import transform_weather_data


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def create_raw_data_directory() -> None:
    """Create the raw-data directory if it does not already exist."""

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def build_raw_record(
    city: dict[str, Any],
    weather_data: dict[str, Any],
) -> dict[str, Any]:
    """Combine city metadata, extraction metadata, and the API response."""

    return {
        "city_name": city["name"],
        "requested_latitude": city["latitude"],
        "requested_longitude": city["longitude"],
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_system": "open_meteo",
        "response_payload": weather_data,
    }


def save_raw_record(
    city_name: str,
    raw_record: dict[str, Any],
) -> Path:
    """Save one raw API response as a JSON file."""

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    safe_city_name = city_name.lower().replace(" ", "_")

    file_name = f"{safe_city_name}_{timestamp}.json"
    file_path = RAW_DATA_DIR / file_name

    with file_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            raw_record,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return file_path


def run_pipeline() -> None:
    """Extract, transform, save, and load weather data."""

    create_raw_data_directory()

    print("Starting weather ETL pipeline...\n")

    all_transformed_records: list[dict[str, Any]] = []

    for city in CITIES:
        city_name = city["name"]

        print(f"Processing {city_name}...")

        try:
            weather_data = fetch_weather_data(
                latitude=city["latitude"],
                longitude=city["longitude"],
            )

            raw_record = build_raw_record(
                city=city,
                weather_data=weather_data,
            )

            saved_file = save_raw_record(
                city_name=city_name,
                raw_record=raw_record,
            )

            transformed_records = transform_weather_data(
                city_name=city_name,
                weather_data=weather_data,
            )

            all_transformed_records.extend(
                transformed_records
            )

            print(f"Raw JSON saved to: {saved_file}")
            print(
                f"Records transformed: "
                f"{len(transformed_records)}"
            )

            if transformed_records:
                print("First transformed record:")
                print(transformed_records[0])

            print()

        except Exception as error:
            print(
                f"Failed to process {city_name}: "
                f"{error}\n"
            )

    if not all_transformed_records:
        print("No transformed records were created.")
        print("Pipeline completed with no output.")
        return

    try:
        csv_file = save_to_csv(
            all_transformed_records
        )

        loaded_records = load_weather_records(
            all_transformed_records
        )

        print(
            f"Total transformed records: "
            f"{len(all_transformed_records)}"
        )
        print(f"CSV saved to: {csv_file}")
        print(
            f"Records loaded into PostgreSQL: "
            f"{loaded_records}"
        )
        print("Pipeline completed successfully.")

    except Exception as error:
        print(
            "Pipeline failed while saving or loading "
            f"the transformed data: {error}"
        )


if __name__ == "__main__":
    run_pipeline()