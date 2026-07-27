"""PostgreSQL database operations for the Weather ETL pipeline."""

from typing import Any

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from src.utils.config import get_database_config
from src.utils.logger import logger


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS weather_hourly (
    id BIGSERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    weather_timestamp TIMESTAMP NOT NULL,
    temperature_2m DOUBLE PRECISION,
    relative_humidity_2m DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    wind_speed_10m DOUBLE PRECISION,
    source_system VARCHAR(100) NOT NULL,
    extracted_at_utc TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_city_weather_timestamp
        UNIQUE (city_name, weather_timestamp)
);
"""


INSERT_WEATHER_QUERY = """
INSERT INTO weather_hourly (
    city_name,
    weather_timestamp,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m,
    source_system,
    extracted_at_utc
)
VALUES (
    %(city_name)s,
    %(weather_timestamp)s,
    %(temperature_2m)s,
    %(relative_humidity_2m)s,
    %(precipitation)s,
    %(wind_speed_10m)s,
    %(source_system)s,
    %(extracted_at_utc)s
)
ON CONFLICT (city_name, weather_timestamp)
DO UPDATE SET
    temperature_2m = EXCLUDED.temperature_2m,
    relative_humidity_2m = EXCLUDED.relative_humidity_2m,
    precipitation = EXCLUDED.precipitation,
    wind_speed_10m = EXCLUDED.wind_speed_10m,
    source_system = EXCLUDED.source_system,
    extracted_at_utc = EXCLUDED.extracted_at_utc,
    updated_at = CURRENT_TIMESTAMP;
"""


def get_database_connection() -> Connection:
    """Create and return a PostgreSQL database connection."""

    database_config = get_database_config()

    return psycopg.connect(
        **database_config,
        row_factory=dict_row,
    )


def create_weather_table(
    connection: Connection,
) -> None:
    """Create the weather_hourly table if it does not exist."""

    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_QUERY)

    connection.commit()

    logger.info(
        "Verified PostgreSQL table: weather_hourly"
    )


def test_database_connection() -> None:
    """Test whether PostgreSQL can be reached."""

    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        current_database() AS database_name,
                        current_user AS database_user,
                        version() AS postgres_version;
                    """
                )

                result = cursor.fetchone()

            logger.info(
                "Database connection successful: "
                "database=%s, user=%s",
                result["database_name"],
                result["database_user"],
            )

    except Exception:
        logger.exception(
            "Database connection test failed."
        )
        raise


def load_weather_records(
    records: list[dict[str, Any]],
) -> int:
    """Insert or update transformed weather records in PostgreSQL."""

    if not records:
        logger.warning(
            "No weather records were provided for database loading."
        )
        return 0

    try:
        with get_database_connection() as connection:
            create_weather_table(connection)

            with connection.cursor() as cursor:
                cursor.executemany(
                    INSERT_WEATHER_QUERY,
                    records,
                )

            connection.commit()

        logger.info(
            "Database load completed for %s records",
            len(records),
        )

        return len(records)

    except Exception:
        logger.exception(
            "Failed to load weather records into PostgreSQL."
        )
        raise


if __name__ == "__main__":
    test_database_connection()