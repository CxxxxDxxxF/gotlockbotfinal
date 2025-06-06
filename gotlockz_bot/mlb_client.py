"""Simple MLB API client."""

from datetime import date
import requests


def get_today_games():
    """Return a list of today's MLB games."""
    today = date.today().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    games = []
    for entry in data.get("dates", []):
        for game in entry.get("games", []):
            home = game["teams"]["home"]["team"]["name"]
            away = game["teams"]["away"]["team"]["name"]
            games.append(f"{away} @ {home}")
    return games
