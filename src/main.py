"""Run the weather ETL pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.api_client import fetch_weather_data
from src.csv_writer import save_to_csv
from src.database import load_weather_records
from src.transform import transform_weather_data
from src.utils.config import CITIES, RAW_DATA_DIR
from src.utils.logger import logger
from src.validation import validate_weather_records


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
        "extracted_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_system": "open_meteo",
        "response_payload": weather_data,
    }


def save_raw_record(
    city_name: str,
    raw_record: dict[str, Any],
) -> Path:
    """Save one raw API response as a JSON file."""

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    safe_city_name = (
        city_name
        .strip()
        .lower()
        .replace(" ", "_")
    )

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
    """Run the complete weather ETL pipeline."""

    logger.info("Starting Weather ETL Pipeline")

    create_raw_data_directory()

    all_transformed_records: list[
        dict[str, Any]
    ] = []

    for city in CITIES:
        city_name = city["name"]

        logger.info(
            "Processing city: %s",
            city_name,
        )

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

            logger.info(
                "Raw JSON saved: %s",
                saved_file.name,
            )

            transformed_records = (
                transform_weather_data(
                    city_name=city_name,
                    weather_data=weather_data,
                )
            )

            all_transformed_records.extend(
                transformed_records
            )

            logger.info(
                "%s records transformed for %s",
                len(transformed_records),
                city_name,
            )

            if transformed_records:
                logger.info(
                    "Sample transformed record for %s: %s",
                    city_name,
                    transformed_records[0],
                )
            else:
                logger.warning(
                    "No transformed records created for %s",
                    city_name,
                )

        except Exception:
            logger.exception(
                "Failed to process city: %s",
                city_name,
            )

    if not all_transformed_records:
        logger.warning(
            "No transformed records were created."
        )
        logger.warning(
            "Pipeline completed with no output."
        )
        return

    try:
        validated_records = (
            validate_weather_records(
                all_transformed_records
            )
        )

        logger.info(
            "%s records passed validation",
            len(validated_records),
        )

        csv_file = save_to_csv(
            validated_records
        )

        logger.info(
            "CSV saved to: %s",
            csv_file,
        )

        loaded_records = load_weather_records(
            validated_records
        )

        logger.info(
            "Total transformed records: %s",
            len(all_transformed_records),
        )

        logger.info(
            "Total validated records: %s",
            len(validated_records),
        )

        logger.info(
            "%s records loaded into PostgreSQL",
            loaded_records,
        )

        logger.info(
            "Weather ETL Pipeline completed successfully."
        )

    except Exception:
        logger.exception(
            "Pipeline failed during validation, "
            "CSV saving, or PostgreSQL loading."
        )


if __name__ == "__main__":
    run_pipeline()