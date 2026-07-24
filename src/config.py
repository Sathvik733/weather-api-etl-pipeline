"""Configuration values for the weather ETL project."""

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = [
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