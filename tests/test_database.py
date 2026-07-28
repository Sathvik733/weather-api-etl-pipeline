"""Tests for PostgreSQL database operations."""

from unittest.mock import ANY, MagicMock, patch

import psycopg
import pytest

from src.database import (
    create_weather_table,
    get_database_connection,
    load_weather_records,
)


def configure_connection_context(
    mock_get_connection: MagicMock,
) -> tuple[MagicMock, MagicMock]:
    """Configure a mocked psycopg connection and cursor context manager."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    # get_database_connection() returns the connection.
    mock_get_connection.return_value = mock_connection

    # Handles:
    # with get_database_connection() as connection:
    mock_connection.__enter__.return_value = mock_connection

    # Handles:
    # with connection.cursor() as cursor:
    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    return mock_connection, mock_cursor


def test_create_weather_table_success() -> None:
    """The table-creation query should execute using the given connection."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    create_weather_table(mock_connection)

    mock_cursor.execute.assert_called_once()


@patch("src.database.get_database_connection")
def test_load_weather_records_success(
    mock_get_connection: MagicMock,
    valid_weather_record,
) -> None:
    """Valid weather records should be passed to executemany."""

    mock_connection, mock_cursor = configure_connection_context(
        mock_get_connection
    )

    loaded_count = load_weather_records(
        [valid_weather_record]
    )

    assert loaded_count == 1

    mock_cursor.executemany.assert_called_once()

    executed_query = mock_cursor.executemany.call_args.args[0]
    executed_records = mock_cursor.executemany.call_args.args[1]

    assert isinstance(executed_query, str)
    assert executed_records == [valid_weather_record]


@patch("src.database.get_database_connection")
def test_load_weather_records_multiple_records(
    mock_get_connection: MagicMock,
    valid_weather_record,
) -> None:
    """The loader should return the number of submitted records."""

    second_record = valid_weather_record.copy()
    second_record["city_name"] = "Bengaluru"

    records = [
        valid_weather_record,
        second_record,
    ]

    _, mock_cursor = configure_connection_context(
        mock_get_connection
    )

    loaded_count = load_weather_records(records)

    assert loaded_count == 2

    mock_cursor.executemany.assert_called_once()

    executed_records = (
        mock_cursor.executemany.call_args.args[1]
    )

    assert executed_records == records


@patch("src.database.get_database_connection")
def test_load_weather_records_empty_list(
    mock_get_connection: MagicMock,
) -> None:
    """An empty record list should not open a database connection."""

    loaded_count = load_weather_records([])

    assert loaded_count == 0
    mock_get_connection.assert_not_called()


@patch("src.database.get_database_connection")
def test_load_weather_records_rolls_back_on_failure(
    mock_get_connection: MagicMock,
    valid_weather_record,
) -> None:
    """A database error should propagate from the loader."""

    mock_connection, mock_cursor = configure_connection_context(
        mock_get_connection
    )

    mock_cursor.executemany.side_effect = psycopg.DatabaseError(
        "Insert failed"
    )

    with pytest.raises(
        psycopg.DatabaseError,
        match="Insert failed",
    ):
        load_weather_records(
            [valid_weather_record]
        )

    # A psycopg connection context manager performs rollback when
    # an exception exits the context. We verify that the context
    # received the exception.
    mock_connection.__exit__.assert_called_once()

    exit_arguments = mock_connection.__exit__.call_args.args

    assert exit_arguments[0] is psycopg.DatabaseError


@patch("src.database.psycopg.connect")
@patch("src.database.get_database_config")
def test_get_database_connection_success(
    mock_get_config: MagicMock,
    mock_connect: MagicMock,
) -> None:
    """Database configuration should be supplied to psycopg."""

    mock_get_config.return_value = {
        "host": "localhost",
        "port": 5432,
        "dbname": "weather_etl",
        "user": "postgres",
        "password": "test-password",
    }

    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    result = get_database_connection()

    assert result == mock_connection

    mock_connect.assert_called_once_with(
        host="localhost",
        port=5432,
        dbname="weather_etl",
        user="postgres",
        password="test-password",
        row_factory=ANY,
    )