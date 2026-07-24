"""Starting point for the weather ETL pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.api_client import fetch_weather_data
from src.config import CITIES


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def create_raw_data_directory() -> None:
    """Create the raw-data directory if it does not already exist."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_raw_record(
    city: dict[str, Any],
    weather_data: dict[str, Any],
) -> dict[str, Any]:
    """Combine city information, extraction metadata, and API response."""

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

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
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
    """Fetch and save weather information for all configured cities."""

    create_raw_data_directory()

    print("Starting weather pipeline...\n")

    for city in CITIES:
        city_name = city["name"]

        print(f"Fetching data for {city_name}...")

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

        hourly = weather_data.get("hourly", {})
        timestamps = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])

        print(f"Number of timestamps: {len(timestamps)}")
        print(f"Number of temperatures: {len(temperatures)}")
        print(f"Saved raw file: {saved_file}")
        print()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()