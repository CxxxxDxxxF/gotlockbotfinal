def parse_bet_details(text):
    """
    Parses relevant information from the OCR'd bet slip text.
    Supports: Player props and team moneyline bets.
    """
    # Player prop match (e.g., "Hunter Dobbins Over 2.5 Earned Runs")
    player_line_match = re.search(
        r"([A-Za-z\s\-]+)\s+(Over|Under)\s+([\d\.]+)\s+(Earned Runs|Hits|Strikeouts)",
        text,
        re.IGNORECASE
    )

    # Team matchup match (e.g., "New York Yankees at Boston Red Sox")
    team_line_match = re.search(
        r"([A-Za-z\s]+)\s+at\s+([A-Za-z\s]+)",
        text,
        re.IGNORECASE
    )

    # Odds match (e.g., -115, +100)
    odds_match = re.search(r"([-+]\d{2,4})", text)

    # === Player prop version ===
    if player_line_match and odds_match:
        bet_player = player_line_match.group(1).strip()
        bet_type = f"{player_line_match.group(2)} {player_line_match.group(3)} {player_line_match.group(4)}"
        odds = odds_match.group(1).strip()
        return {
            "game": "Unknown",  # Optional enhancement later
            "bet": f"{bet_player} – {bet_type}",
            "odds": odds
        }

    # === Team moneyline version ===
    elif team_line_match and odds_match:
        team1 = team_line_match.group(1).strip()
        team2 = team_line_match.group(2).strip()
        odds = odds_match.group(1).strip()
        return {
            "game": f"{team1} @ {team2}",
            "bet": f"{team1} – Moneyline",
            "odds": odds
        }

    return None
