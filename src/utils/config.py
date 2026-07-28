"""Central configuration for the weather ETL pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "weather_etl.log"


OPEN_METEO_BASE_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

HOURLY_WEATHER_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]


CITIES = [
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


def get_database_config() -> dict[str, str | int]:
    """Return PostgreSQL connection settings."""

    return {
        "host": os.getenv(
            "DB_HOST",
            "localhost",
        ),
        "port": int(
            os.getenv(
                "DB_PORT",
                "5432",
            )
        ),
        "dbname": os.getenv(
            "DB_NAME",
            "weather_etl",
        ),
        "user": os.getenv(
            "DB_USER",
            "postgres",
        ),
        "password": os.getenv(
            "DB_PASSWORD",
            "postgres",
        ),
    }