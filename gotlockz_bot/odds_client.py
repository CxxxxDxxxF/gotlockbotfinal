import requests
from config import THE_ODDS_API_KEY, JSON_ODDS_KEY

BASE_ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"
JSON_ODDS_BASE = "https://jsonodds.com/api/v2"


def get_all_upcoming_odds(sport: str = "baseball_mlb") -> dict:
    url = f"{BASE_ODDS_API_URL}/{sport}/odds"
    params = {
        "apiKey": THE_ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
    except Exception:
        return {}
    retval = {}
    for game in data:
        away = game["away_team"]
        home = game["home_team"]
        key = f"{away} vs {home}"
        bookmaker = game["bookmakers"][0]
        markets = bookmaker["markets"]
        ml = {}
        spread = None
        total = None
        for m in markets:
            if m["key"] == "h2h":
                for outcome in m["outcomes"]:
                    ml[outcome["name"]] = outcome["price"]
            elif m["key"] == "spreads":
                spread = m["outcomes"][0]["point"]
            elif m["key"] == "totals":
                total = m["outcomes"][0]["point"]
        retval[key] = {"moneyline": ml, "spread": spread, "total": total}
    return retval


def get_line_for_matchup(teamA: str, teamB: str) -> dict:
    all_odds = get_all_upcoming_odds()
    key = f"{teamA} vs {teamB}"
    return all_odds.get(key)


def get_player_prop(player_name: str, stat_key: str) -> dict:
    url = f"{JSON_ODDS_BASE}/proposition"
    params = {"apiKey": JSON_ODDS_KEY, "player": player_name}
    try:
        data = requests.get(url, params=params, timeout=10).json()
    except Exception:
        return {}
    return data.get("data", {}).get(stat_key.lower(), {})
