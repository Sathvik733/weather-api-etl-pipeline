"""Central configuration for the Weather ETL pipeline."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


# Load environment variables from the project-level .env file.
load_dotenv()


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "weather_etl.log"


# Open-Meteo API configuration
OPEN_METEO_BASE_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

HOURLY_WEATHER_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]


# Cities processed by the pipeline
CITIES: list[dict[str, Any]] = [
    {
        "name": "Hyderabad",
        "latitude": 17.3850,
        "longitude": 78.4867,
    },
    {
        "name": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
    },
]


def get_database_config() -> dict[str, str]:
    """Return PostgreSQL configuration from environment variables."""

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        missing_names = ", ".join(missing_variables)

        raise ValueError(
            "Missing required environment variables: "
            f"{missing_names}"
        )

    return {
        "host": os.environ["DB_HOST"],
        "port": os.environ["DB_PORT"],
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }