"""Utilities for researching MLB teams."""

import requests


def team_info(team: str):
    """Return basic information about an MLB team."""
    resp = requests.get("https://statsapi.mlb.com/api/v1/teams?sportId=1", timeout=10)
    resp.raise_for_status()
    for t in resp.json().get("teams", []):
        if team.lower() in t["name"].lower():
            return t
    return {}
