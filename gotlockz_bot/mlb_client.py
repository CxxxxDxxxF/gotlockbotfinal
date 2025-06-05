import requests
from datetime import datetime
from config import MLB_STATS_API_KEY

BASE_URL = "https://statsapi.mlb.com/api/v1"


def get_today_schedule():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/schedule?sportId=1&date={today}"
    try:
        resp = requests.get(url, timeout=10).json()
    except Exception:
        return {}
    games_dict = {}
    for game in resp.get('dates', [{}])[0].get('games', []):
        away = game['teams']['away']['team']['name']
        home = game['teams']['home']['team']['name']
        key = f"{away} vs {home}"
        games_dict[key] = {
            'gamePk': game['gamePk'],
            'gameDate': game['gameDate'],
            'venue': game['venue']['name']
        }
    return games_dict


def get_probable_starter(team_name: str) -> str:
    schedule = get_today_schedule()
    for matchup, info in schedule.items():
        away, home = matchup.split(' vs ')
        if team_name in (away, home):
            gamePk = info['gamePk']
            box_url = f"{BASE_URL}/game/{gamePk}/preview"
            try:
                data = requests.get(box_url, timeout=10).json()
                away_p = data['probablePitchers']['away']['fullName']
                home_p = data['probablePitchers']['home']['fullName']
                return away_p if team_name == away else home_p
            except Exception:
                return None
    return None


def get_last_five_stats(pitcher_name: str) -> dict:
    return {"name": pitcher_name, "ERA": 2.85, "WHIP": 1.05, "K9": 8.2}


def get_team_metrics(team_name: str) -> dict:
    return {
        "team": team_name,
        "RS": 700,
        "RA": 650,
        "RPG": 700 / 162,
        "BA_vs_RHP": 0.265,
        "BA_vs_LHP": 0.254,
        "BP_ERA_14": 3.55,
        "probable_starter": get_probable_starter(team_name),
    }


def get_proj_win_pct(team_name: str) -> float:
    metrics = get_team_metrics(team_name)
    rs, ra = metrics['RS'], metrics['RA']
    return rs ** 2 / (rs ** 2 + ra ** 2)
