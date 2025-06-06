"""HTTP client for fetching odds data."""

import requests


def fetch_odds(url: str):
    """Fetch JSON odds data from the given API URL."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
