from typing import Any


async def search_flights(origin: str, destination: str) -> list[dict[str, Any]]:
    return [
        {'carrier': 'SkyFast', 'price': 420.0, 'duration_hours': 7.5, 'stops': 1},
        {'carrier': 'AeroMax', 'price': 510.0, 'duration_hours': 6.0, 'stops': 0},
    ]


async def search_hotels(destination: str) -> list[dict[str, Any]]:
    return [
        {'name': f'{destination} Central Suites', 'nightly_rate': 180.0, 'rating': 4.6},
        {'name': f'{destination} Budget Inn', 'nightly_rate': 95.0, 'rating': 4.1},
    ]


async def get_weather_risk(destination: str) -> dict[str, Any]:
    return {'destination': destination, 'storm_probability': 0.12, 'advisory_level': 'low'}
