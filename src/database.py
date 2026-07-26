"""PostgreSQL connection and loading utilities."""

import os
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg import Connection


load_dotenv()


class DatabaseConfigurationError(Exception):
    """Raised when required database configuration is missing."""


def get_database_config() -> dict[str, str]:
    """Read PostgreSQL configuration from environment variables."""

    config = {
        "host": os.getenv("DB_HOST", ""),
        "port": os.getenv("DB_PORT", ""),
        "dbname": os.getenv("DB_NAME", ""),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
    }

    missing_values = [
        key
        for key, value in config.items()
        if not value
    ]

    if missing_values:
        missing_names = ", ".join(missing_values)

        raise DatabaseConfigurationError(
            f"Missing database configuration: {missing_names}"
        )

    return config


def get_database_connection() -> Connection:
    """Create and return a PostgreSQL connection."""

    config = get_database_config()

    return psycopg.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
    )


def test_database_connection() -> None:
    """Verify that Python can connect to PostgreSQL."""

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    current_database(),
                    current_user,
                    version();
                """
            )

            database_name, username, version = cursor.fetchone()

            print("Database connection successful.")
            print(f"Database: {database_name}")
            print(f"User: {username}")
            print(f"PostgreSQL: {version}")
def load_weather_records(
    records: list[dict[str, Any]],
) -> int:
    """Insert transformed weather records into PostgreSQL."""

    if not records:
        return 0

    insert_query = """
        INSERT INTO weather_hourly (
            city_name,
            weather_timestamp,
            temperature_celsius,
            relative_humidity_percent,
            precipitation_mm
        )
        VALUES (
            %(city_name)s,
            %(weather_timestamp)s,
            %(temperature_celsius)s,
            %(relative_humidity_percent)s,
            %(precipitation_mm)s
        )
        ON CONFLICT (
            city_name,
            weather_timestamp
        )
        DO UPDATE SET
            temperature_celsius =
                EXCLUDED.temperature_celsius,
            relative_humidity_percent =
                EXCLUDED.relative_humidity_percent,
            precipitation_mm =
                EXCLUDED.precipitation_mm;
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                insert_query,
                records,
            )

        connection.commit()

    return len(records)

if __name__ == "__main__":
    test_database_connection()